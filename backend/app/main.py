from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.core.rag_logic import rag_engine
from app.core.ai_client import ai_client
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import shutil
import os
import json
import logging
from app.core.logger import logger
from app.core.templates import (
  TZ_STRUCTURE_TEMPLATE, 
  SYSTEM_GENERATION_INSTRUCTION, 
  SYSTEM_QA_INSTRUCTION, 
  FEW_SHOT_EXAMPLES,
  SECTION_SPECIFIC_INSTRUCTIONS,
  JSON_INSTRUCTIONS,
  FORMATING_STYLE
)
from app.core.schemas import TZSection, TZDocument
from app.core.utils import SECTION_CONTEXT_MAPPING

@asynccontextmanager
async def lifespan(app: FastAPI):
  try:
    logging.info("Db initialize")
    await rag_engine.init_db()
    logging.info("DB ready")
  except Exception as e:
    logger.error(f"DB error: {e}")
  yield
  logging.info("Server stopped")

app = FastAPI(
    title="ENFORENCE AI Engine", 
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

class MessageContent(BaseModel):
  type: str = "text"
  text: str

class Message(BaseModel):
  role: str
  content: List[MessageContent]

class TaskMetadata(BaseModel):
  project_id: Optional[str] = None
  tz_structure_version: str = "UA-205-v1"
  language: str = "uk"
  project_domain: Optional[str] = None

class ContextData(BaseModel):
  questionnaire: Dict[str, Any]
  retrieved_chunks: Optional[List[Dict[str, Any]]] = []
  task_metadata: Optional[TaskMetadata] = None
  target_sections: Optional[List[str]] = Field(default=["1", "2", "3"])

class GenerateSpecRequest(BaseModel):
  mode: str
  messages: List[Message]
  context: ContextData

@app.post("/api/upload")
async def upload_project_doc(project_id: str, file: UploadFile = File(...)):
  temp_path = f"temp_{file.filename}"
  with open(temp_path, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)
  
  chunks_count = await rag_engine.ingest_docx(project_id, temp_path)
  os.remove(temp_path)
  
  return {"status": "ok", "project_id": project_id, "chunks_indexed": chunks_count}

@app.post("/api/generate")
async def generate_spec(data: GenerateSpecRequest):
  target_ids = data.context.target_sections or [str(i) for i in range(1, 11)]

  rag_context = ""
  questionnaire_text = json.dumps(data.context.questionnaire, ensure_ascii=False, indent=2)

  if data.mode == "qa_navigation":
    user_query = data.messages[-1].content[0].text if isinstance(data.messages[-1].content, list) else data.messages[-1].content
    logger.info(f"[RAG START] User query: '{user_query}'")
    project_id = data.context.task_metadata.project_id if data.context.task_metadata else None
    if project_id:
      raw_chunks = await rag_engine.get_context(user_query, project_id=project_id, scope="project", limit=30)
      logger.info(f"[RAG RAW] Знайдено кандидатів: {len(raw_chunks)}")
      
      for i, c in enumerate(raw_chunks[:3]):
        logger.info(f"   👉 Candidate #{i+1}: Score={c.get('score'):.4f} | Text='{c['content'][:40]}...'")

      THRESHOLD = 0.4
      filtered_chunks = [c for c in raw_chunks if c.get('score', 0) > THRESHOLD][:10]

      logger.info(f"[RAG FILTER] Після порогу {THRESHOLD}: залишилось {len(filtered_chunks)}")

      if filtered_chunks:
        rag_context = "\n\n".join([f"Фрагмент документу: {c['content']}" for c in filtered_chunks])
      else:
        rag_context = "Інформація в документах проекту відсутня."
        logger.warning("WARNING: All documents above THRESHOLD!")
    
    if not any(m.role == "system" for m in data.messages):
      data.messages.insert(0, {
        "role": "system", 
        "content": [{"type": "text", "text": f"{SYSTEM_QA_INSTRUCTION}\n\nКОНТЕКСТ:\n{rag_context}"}]
      })

  elif data.mode == "generate_tz":
    first_target = target_ids[0] if target_ids else "1"
    section_title = TZ_STRUCTURE_TEMPLATE.get(first_target, {}).get("title", "") if isinstance(TZ_STRUCTURE_TEMPLATE.get(first_target), dict) else ""

    reg_query = f"Вимоги до змісту розділу '{first_target} {section_title}' згідно Постанови 205 Додаток 3"
    reg_chunks = await rag_engine.get_context(reg_query, project_id="SYSTEM_REGULATIONS", scope="system", limit=3)

    ref_query = f"Приклад змісту розділу '{first_target} {section_title}' з технічними деталями та таблицями"
    ref_chunks = await rag_engine.get_context(ref_query, project_id="TEMPLATE_TZ", scope="project", limit=2)

    if reg_chunks:
      reg_text = "\n".join([f"--- Нормативна вимога ---\n{c['content']}" for c in reg_chunks])
    else:
      reg_text = "Специфічні вимоги не знайдені. Використовуй загальні стандарти ДСТУ 3008:2015."

    if ref_chunks:
      ref_text = "\n".join([f"--- ЗРАЗОК З РЕФЕРЕНСНОГО ТЗ ---\n{c['content']}" for c in ref_chunks])
    else:
      ref_text = "Приклади відсутні. Використовуй стандартний офіційний стиль."
    
    if first_target.startswith("3") or first_target == "3":
      chosen_example = FEW_SHOT_EXAMPLES["requirements"]
    elif first_target in ["7", "8", "9"]:
      chosen_example = FEW_SHOT_EXAMPLES["docs"]
    else:
      chosen_example = FEW_SHOT_EXAMPLES["default"]

    try:
      full_q_data = json.loads(json.dumps(data.context.questionnaire, ensure_ascii=False))
      clean_full_data = clean_empty_fields(full_q_data)
      final_context_data = {}
        
      needed_keys = set()
      for tid in target_ids:
        base_id = tid.split('.')[0]
        needed_keys.update(SECTION_CONTEXT_MAPPING.get(base_id, []))

      if not needed_keys:
        final_context_data = clean_full_data
      else:
        for key in needed_keys:
          if key in clean_full_data:
            final_context_data[key] = clean_full_data[key]
        if "project_info" in clean_full_data:
          if "project_info" not in final_context_data:
            final_context_data["project_info"] = {}
          final_context_data["project_info"]["basic_data"] = clean_full_data["project_info"].get("basic_data", {})

      optimized_questionnaire_text = json.dumps(final_context_data, ensure_ascii=False, indent=2)
    except Exception as e:
      logger.warning(f"Optimization failed: {e}")
      optimized_questionnaire_text = questionnaire_text

    base_section_id = first_target.split('.')[0]
    specific_instruction = SECTION_SPECIFIC_INSTRUCTIONS.get(
      base_section_id, 
      "ФОКУС: Дотримуйся структури розділу та вимог ДСТУ 3008."
    )

    formatted_system_prompt = SYSTEM_GENERATION_INSTRUCTION.format(
      section_instruction=specific_instruction,
      selected_example=chosen_example,
      JSON_INSTRUCTIONS=JSON_INSTRUCTIONS,
      FORMATING_STYLE=FORMATING_STYLE
    )

    final_system_prompt = (
      f"{formatted_system_prompt}\n\n"
      
      f"### ЗАКОНОДАВСТВО (ОБОВ'ЯЗКОВО):\n"
      f"{reg_text}\n\n"

      f"### ПРИКЛАД ОФОРМЛЕННЯ (СТИЛЬ):\n"
      f"УВАГА: Використовуй цей стиль і таблиці, АЛЕ НЕ ДАНІ.\n"
      f"{ref_text}\n\n"

      f"### ДАНІ ПРОЄКТУ (ДЖЕРЕЛО ФАКТІВ):\n"
      f"{optimized_questionnaire_text}\n"
    )

    logger.info(f"[RAG GENERATION] {final_system_prompt}")

    new_messages = [{"role": "system", "content": [{"type": "text", "text": final_system_prompt}]}]
    
    new_messages.append({
      "role": "user", 
      "content": [{"type": "text", "text": f"Згенеруй розділи {', '.join(target_ids)} у JSON."}]
    })
    
    data.messages = new_messages
  
  raw_response = await ai_client.generate_structured_response(data, rag_context_str=rag_context)

  if raw_response.get("status") == "error":
    return raw_response

  if data.mode == "generate_tz":
    try:
      output_data = raw_response.get("output", {})
      document_data = output_data.get("document") if isinstance(output_data, dict) else {}
      
      if not document_data:
        if "raw_output" in raw_response:
          document_data = {"sections": [], "content": raw_response["raw_output"]}
        else:
          raise ValueError("Модель не повернула структуру 'document'")

      validated_doc = TZDocument(**document_data)
      
      existing_codes = {s.code for s in validated_doc.sections}
      
      for code in target_ids:
        if code not in existing_codes:
          sec_def = TZ_STRUCTURE_TEMPLATE.get(code, "Розділ")
          sec_name = sec_def["title"] if isinstance(sec_def, dict) else sec_def

          validated_doc.sections.append(TZSection(
            code=code,
            name=sec_name,
            content="Розділ не був згенерований моделлю. Спробуйте повторити запит.",
            status="incomplete"
          ))
      
      def sort_key(x):
        try:
          return [int(part) for part in x.code.split('.')]
        except:
          return 999
      validated_doc.sections.sort(key=sort_key)
      
      raw_response["output"]["document"]["sections"] = [s.dict() for s in validated_doc.sections]
      raw_response["output"]["diagnostics"] = {
        "rag_source": "SYSTEM_REGULATIONS" if rag_context else "None",
        "thought_process": output_data.get("thought_process", "N/A")
      }

    except Exception as e:
      logger.error(f"Validation error: {e}")
      raw_response["output"] = {"error": str(e), "document": {"sections": []}}
  
  return raw_response

@app.get("/api/health/ai")
async def health_check_ai():
  return await ai_client.check_connection()

@app.get("/api/projects")
async def list_projects():
  try:
    projects = await rag_engine.get_all_projects()
    return {"projects": projects}
  except Exception as e:
    logger.error(f"Error loading list of projects: {e}")
    return {"projects": []}

def clean_empty_fields(data):
  if isinstance(data, dict):
    return {
      k: v 
      for k, v in ((k, clean_empty_fields(v)) for k, v in data.items()) 
      if v not in (None, "", {}, [])
    }
  if isinstance(data, list):
    return [v for v in map(clean_empty_fields, data) if v not in (None, "", {}, [])]
  return data