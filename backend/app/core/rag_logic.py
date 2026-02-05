from app.core.logger import logger
import os
from docx import Document
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, Text, String, select, text, func
from sqlalchemy.orm import declarative_base
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

Base = declarative_base()

class ProjectChunk(Base):
  __tablename__ = 'project_chunks'
  id = Column(Integer, primary_key=True)
  project_id = Column(String, index=True)
  content = Column(Text)
  embedding = Column(Vector(768))

class RAGEngine:
  def __init__(self):
    self.url = os.getenv("DATABASE_URL")
    self.engine = create_async_engine(self.url)
    self.async_session = sessionmaker(self.engine, class_=AsyncSession)
    self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

  async def ingest_docx(self, project_id: str, file_path: str):
    doc = Document(file_path)
    full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=800, 
      chunk_overlap=150
    )

    logger.info(f"Start downloading: {project_id}")
    texts = text_splitter.split_text(full_text)
    logger.info(f"Document splitted {len(texts)} chanks.")

    async with self.async_session() as session:
      for text in texts:
        vector = self.embeddings.embed_query(text)
        chunk = ProjectChunk(
          project_id=project_id,
          content=text,
          embedding=vector
        )
        session.add(chunk)
      await session.commit()
    logger.info(f"All chunks downloaded in pgvector.")
    return len(texts)
  
  async def init_db(self):
    async with self.engine.begin() as conn:
      await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
      await conn.run_sync(Base.metadata.create_all)
    logging.info("DB table is created")

  async def get_context(self, query: str, project_id: str = None):
    query_vector = self.embeddings.embed_query(query)
    async with self.async_session() as session:
      stmt = select(ProjectChunk).order_by(
        ProjectChunk.embedding.cosine_distance(query_vector)
      ).limit(3)
      
      if project_id:
        stmt = stmt.where(ProjectChunk.project_id == project_id)
      
      result = await session.execute(stmt)
      return [{"id": str(c.id), "content": c.content} for c in result.scalars().all()]

  async def get_all_projects(self):
    async with self.async_session() as session:
      try:
        stmt = select(ProjectChunk.project_id).distinct() 
        result = await session.execute(stmt)
        
        return [row[0] for row in result.all()]
      except Exception as e:
        logger.error(f"Error while doqnloading projects: {e}")
        return []

rag_engine = RAGEngine()