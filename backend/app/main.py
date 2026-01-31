from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.rag_logic import rag_engine
from app.core.ai_client import ai_client

app = FastAPI(title="ENFORENCE AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
  description: str

@app.post("/api/generate")
async def generate_spec(data: QueryRequest):
  context = rag_engine.get_context(data.description)
  
  generated_text = await ai_client.generate_response(
    prompt=data.description,
    context=context
  )
  
  return {
    "status": "success",
    "generated_text": generated_text,
    "context_used": context
  }

@app.get("/api/health/ai")
async def health_check_ai():
  result = await ai_client.check_connection()
  return result

@app.post("/api/ingest")
async def start_ingestion(background_tasks: BackgroundTasks):
  background_tasks.add_task(rag_engine.ingest_documents, "./data_source")
  return {"message": "Процес індексації запущено у фоновому режимі."}