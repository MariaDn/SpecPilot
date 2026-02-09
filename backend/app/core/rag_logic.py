import time
import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional

from sqlalchemy import Column, Integer, Text, String, select, text, func, Index
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector

from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader

from app.core.hybrid_retriever import HybridRetriever
from app.core.logger import logger

Base = declarative_base()

class ProjectChunk(Base):
  __tablename__ = 'project_chunks'
  id = Column(Integer, primary_key=True)
  project_id = Column(String, index=True)
  content = Column(Text)
  embedding = Column(Vector(768))
  search_vector = Column(TSVECTOR)
  logging.basicConfig(level=logging.INFO)

  __table_args__ = (
    Index('idx_project_chunks_search_vector', 'search_vector', postgresql_using='gin'),
  )

class RAGEngine:
  def __init__(self):
    self.url = os.getenv("DATABASE_URL")
    self.engine = create_async_engine(self.url)
    self.async_session = sessionmaker(self.engine, class_=AsyncSession)
    self.embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
    self.retriever = HybridRetriever()

    self.text_splitter = SemanticChunker(
      self.embeddings,
      breakpoint_threshold_type="percentile",
      buffer_size=3
    )

  async def ingest_docx(self, project_id: str, file_path: str):
    overall_start = time.perf_counter()
    
    # 1. Loading the document
    start_time = time.perf_counter()
    loader = Docx2txtLoader(file_path)
    documents = loader.load()
    load_duration = time.perf_counter() - start_time
    logger.info(f"Step 1/3: Document loaded in {load_duration:.4f} seconds.")
    
    # 2. Semantic Chunking
    start_time = time.perf_counter()
    # Uses SemanticChunker with percentile threshold and buffer_size=3
    chunks = self.text_splitter.split_documents(documents)
    chunk_duration = time.perf_counter() - start_time
    logger.info(f"Step 2/3: Semantic chunking completed in {chunk_duration:.4f} seconds. Created {len(chunks)} chunks.")
    
    # 3. Embedding generation and DB storage
    start_time = time.perf_counter()
    async with self.async_session() as session:
      for chunk_doc in chunks:
        text_content = chunk_doc.page_content

        # Generate embedding using all-mpnet-base-v2 model (768 dimensions)
        vector = self.embeddings.embed_query(text_content)

        # Prepare data for Hybrid Search (Vector + TSVector)
        db_chunk = ProjectChunk(
          project_id=project_id,
          content=text_content,
          embedding=vector,
          # tsvector for Ukrainian language support
          search_vector=func.to_tsvector('ukrainian', text_content)
        )
        session.add(db_chunk)
      await session.commit()

    db_duration = time.perf_counter() - start_time
    total_duration = time.perf_counter() - overall_start
    
    logger.info(f"Step 3/3: Database indexing (embedding + tsvector) finished in {db_duration:.4f} seconds.")
    logger.info(f"TOTAL processing time for project '{project_id}': {total_duration:.4f} seconds.")
    return len(chunks)
  
  async def init_db(self):
    async with self.engine.begin() as conn:
      await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
      await conn.run_sync(Base.metadata.create_all)
    logging.info("DB table is created")


  async def get_context(self, query: str, project_id: str = None, search_mode: str = "hybrid", limit: int = 5):
    query_vector = self.embeddings.embed_query(query)

    async with self.async_session() as session:
      vec_res = []
      key_res = []

      # 1. Vector search (Cosine Distance)
      if search_mode in ["vector", "hybrid"]:
        vec_stmt = select(ProjectChunk).order_by(
          ProjectChunk.embedding.cosine_distance(query_vector)
        ).limit(15)
        if project_id:
          vec_stmt = vec_stmt.where(ProjectChunk.project_id == project_id)
        vec_res = (await session.execute(vec_stmt)).scalars().all()
      
      # 2. Full text search (BM25-like)
      if search_mode in ["keyword", "hybrid"]:
        ts_query = func.websearch_to_tsquery('ukrainian', query)
        keyword_stmt = select(ProjectChunk).where(
          ProjectChunk.search_vector.op('@@')(ts_query)
        ).order_by(
          func.ts_rank_cd(ProjectChunk.search_vector, ts_query).desc()
        ).limit(15)
        if project_id:
          keyword_stmt = keyword_stmt.where(ProjectChunk.project_id == project_id)
        key_res = (await session.execute(keyword_stmt)).scalars().all()

      if search_mode == "vector":
        final_docs = vec_res[:limit]
      elif search_mode == "keyword":
        final_docs = key_res[:limit]
      else:
        # HybridRetriever for RRF
        final_docs = await self.retriever.rrf_merge(vec_res, key_res)
        final_docs = final_docs[:limit]

      # top-5 results
      return [{"id": str(c.id), "content": c.content} for c in final_docs[:5]]

  async def get_all_projects(self):
    async with self.async_session() as session:
      try:
        stmt = select(ProjectChunk.project_id).distinct() 
        result = await session.execute(stmt)
        
        return [row[0] for row in result.all()]
      except Exception as e:
        logger.error(f"Error while downloading projects: {e}")
        return []

rag_engine = RAGEngine()