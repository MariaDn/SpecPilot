from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.rag_logic import rag_engine
from app.core.ai_client import ai_client
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import shutil
import os
from app.core.logger import logger

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
  if data.mode == "qa_navigation":
    search_query = data.messages[-1].content[0].text
  else:
    search_query = data.context.questionnaire.get("project_info", {}).get("goals", {}).get("problem_statement", "")

  project_id = data.context.task_metadata.project_id if data.context.task_metadata else None
  retrieved_chunks = await rag_engine.get_context(search_query, project_id=project_id)
    
  data.context.retrieved_chunks = retrieved_chunks
  return await ai_client.generate_structured_response(data)

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