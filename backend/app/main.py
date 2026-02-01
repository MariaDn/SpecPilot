from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.rag_logic import rag_engine
from app.core.ai_client import ai_client
from typing import Dict, Any, Optional

app = FastAPI(title="ENFORENCE AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
  mode: str
  questionnaire: Dict[str, Any]

@app.post("/api/generate")
async def generate_spec(data: GenerateRequest):
    search_query = data.questionnaire.get("project_info", {}).get("goals", {}).get("problem_statement", "")
    
    rag_context = rag_engine.get_context(search_query) if search_query else []
    
    generated_text = await ai_client.generate_response(
        questionnaire=data.questionnaire,
        rag_chunks=rag_context
    )
    
    return {
        "status": "success",
        "generated_text": generated_text,
        "rag_context": rag_context
    }

@app.get("/api/health/ai")
async def health_check_ai():
  result = await ai_client.check_connection()
  return result

@app.post("/api/ingest")
async def start_ingestion(background_tasks: BackgroundTasks):
  background_tasks.add_task(rag_engine.ingest_documents, "./data_source")
  return {"message": "Процес індексації запущено у фоновому режимі."}