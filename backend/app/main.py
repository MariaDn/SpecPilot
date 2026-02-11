from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.core.rag_logic import rag_engine
from app.core.ai_client import ai_client
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import shutil
import os
import logging
from app.core.logger import logger
from templates import TZ_STRUCTURE_TEMPLATE, SYSTEM_GENERATION_INSTRUCTION, SYSTEM_QA_INSTRUCTION, JSON_INSTRUCTIONS

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

  if data.mode == "qa_navigation":
    user_query = data.messages[-1].content[0].text if isinstance(data.messages[-1].content, list) else data.messages[-1].content
  else:
    problem = data.context.questionnaire.get("project_info", {}).get("goals", {}).get("problem_statement", "")
    user_query = f"{problem} розділи ТЗ: {', '.join(target_ids)}"

  project_id = data.context.task_metadata.project_id if data.context.task_metadata else None
  retrieved_chunks = await rag_engine.get_context(user_query, project_id=project_id)  
  filtered_chunks = [c for c in retrieved_chunks if c.score > 0.6][:5]
  data.context.retrieved_chunks = filtered_chunks

  if data.mode == "generate_tz":
    target_structure = {k: v for k, v in TZ_STRUCTURE_TEMPLATE.items() if k in target_ids}
    sections_info = "\n".join([
      f"{k}. {v if isinstance(v, str) else v['title']}" 
      for k, v in target_structure.items()
    ])


    focus_instruction = (
      f"{SYSTEM_GENERATION_INSTRUCTION}\n\n"
      f"{JSON_INSTRUCTIONS}\n\n"
      f"ЗАРАЗ ГЕНЕРУЙ ТІЛЬКИ РОЗДІЛИ: {', '.join(target_ids)}.\n"
      f"СТРУКТУРА ЦИХ РОЗДІЛІВ:\n{sections_info}"
    )

    new_messages = [{"role": "system", "content": [{"type": "text", "text": focus_instruction}]}]
        
    history = [m.dict() if hasattr(m, 'dict') else m for m in data.messages if (m.role if hasattr(m, 'role') else m.get('role')) != "system"]
    new_messages.extend(history[-2:])
    
    new_messages.append({"role": "user", "content": [{"type": "text", "text": f"Дані опитувальника: {data.context.questionnaire}\n\nЗгенеруй розділи у JSON."}]})
    data.messages = new_messages
      
  elif data.mode == "qa_navigation":
    if not any(m.role == "system" for m in data.messages):
      data.messages.insert(0, {
        "role": "system", 
        "content": [{"type": "text", "text": f"{SYSTEM_QA_INSTRUCTION}"}]
      })
  
  raw_response = await ai_client.generate_structured_response(data)

  if raw_response.get("status") == "error":
    return raw_response

  if data.mode == "generate_tz":
    try:
      output_data = raw_response.get("output", {})
      document_data = output_data.get("document") if isinstance(output_data, dict) else {}
      
      if not document_data:
        raise ValueError("Модель не повернула структуру 'document'")

      validated_doc = TZDocument(**document_data)
      
      existing_codes = {s.code for s in validated_doc.sections}
      
      for code in target_ids:
        if code not in existing_codes:
          validated_doc.sections.append(TZSection(
            code=code,
            name=TZ_STRUCTURE_TEMPLATE[code] if isinstance(TZ_STRUCTURE_TEMPLATE[code], str) else TZ_STRUCTURE_TEMPLATE[code]["title"],
            content="Розділ не був згенерований моделлю. Спробуйте повторити запит.",
            status="incomplete"
          ))
      
      validated_doc.sections.sort(key=lambda x: float(x.code.split('.')[0]) if '.' in x.code else float(x.code))
      
      raw_response["output"]["document"]["sections"] = [s.dict() for s in validated_doc.sections]
      raw_response["output"]["diagnostics"] = {
          "confidence_overall": 0.85,
          "target_sections": target_ids,
          "missing_in_step": list(set(target_ids) - existing_codes)
      }

    except Exception as e:
      logger.error(f"Validation error: {e}")
  
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