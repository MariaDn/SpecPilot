import time
import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional
import re

from sqlalchemy import Column, Integer, Text, String, select, text, func, Index
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
from sqlalchemy import or_

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
    self.base_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200,
      separators=["\n\n", "\n", "Таблиця", "FR-", ". "]
    )

    self.text_splitter = SemanticChunker(
      self.embeddings,
      breakpoint_threshold_type="standard_deviation",
      breakpoint_threshold_amount=0.8,
      buffer_size=1
    )

  async def ingest_docx(self, project_id: str, file_path: str):
    overall_start = time.perf_counter()
    
    # 1. Loading the document
    start_time = time.perf_counter()
    loader = Docx2txtLoader(file_path)
    documents = loader.load()
    intermediate_docs = self.base_splitter.split_documents(documents)
    load_duration = time.perf_counter() - start_time
    logger.info(f"Step 1/3: Document loaded in {load_duration:.4f} seconds.")
    
    # 2. Semantic Chunking
    start_time = time.perf_counter()
    # Uses SemanticChunker with percentile threshold and buffer_size=3
    chunks = self.text_splitter.split_documents(intermediate_docs)
    # chunks = self.text_splitter.split_documents(documents)
    for i, chunk in enumerate(chunks[:3]):
      logger.info(f"Chunk {i} length: {len(chunk.page_content)} chars. Preview: {chunk.page_content[:50]}...")
    chunk_duration = time.perf_counter() - start_time
    logger.info(f"Step 2/3: Semantic chunking completed in {chunk_duration:.4f} seconds. Created {len(chunks)} chunks.")
    
    # 3. Embedding generation and DB storage
    start_time = time.perf_counter()
    async with self.async_session() as session:
      for chunk_doc in chunks:
        text_content = chunk_doc.page_content

        # Generate embedding using all-mpnet-base-v2 model (768 dimensions)
        contextual_text = f"Проект: {project_id}. Зміст: {chunk_doc.page_content}"
        vector = self.embeddings.embed_query(contextual_text)

        # Prepare data for Hybrid Search (Vector + TSVector)
        db_chunk = ProjectChunk(
          project_id=project_id,
          content=text_content,
          embedding=vector
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


  async def get_context(self, query: str, project_id: str = None, search_mode: str = "hybrid", limit: int = 5, scope: str = "project"):
    query_vector = self.embeddings.embed_query(query)

    async with self.async_session() as session:
      vec_res = []
      key_res = []

      # 1. Vector search (Cosine Distance)
      if search_mode in ["vector", "hybrid"]:
        vec_stmt = select(ProjectChunk, ProjectChunk.embedding.cosine_distance(query_vector).label("distance"))

        if scope == "project" and project_id:
          vec_stmt = vec_stmt.where(ProjectChunk.project_id == project_id)
        elif scope == "system":
          vec_stmt = vec_stmt.where(ProjectChunk.project_id == "SYSTEM_REGULATIONS")
        elif scope == "all" and project_id:
          vec_stmt = vec_stmt.where(or_(
            ProjectChunk.project_id == project_id,
            ProjectChunk.project_id == "SYSTEM_REGULATIONS"
          ))

        vec_stmt = vec_stmt.order_by("distance").limit(50)
        result = await session.execute(vec_stmt)
        for chunk, dist in result.all():
          chunk.score = 1 - dist
          vec_res.append(chunk)
      
      # 2. Full text search (BM25-like)
      if search_mode in ["keyword", "hybrid"]:
        clean_query = query.replace('?', '').replace('!', '').replace('(', '').replace(')', '')
        words = [w for w in clean_query.split() if len(w) > 2]
        ts_query_string = " | ".join(words) if words else ""

        numbers = re.findall(r'\d+(?:\.\d+)?', clean_query)
        if numbers:
          num_query = " & ".join(numbers)
          if ts_query_string:
            ts_query_string = f"({num_query}) & ({ts_query_string})"
          else:
            ts_query_string = num_query

        if ts_query_string:
          ts_query = func.to_tsquery('ukrainian', ts_query_string)
        else:
          ts_query = func.websearch_to_tsquery('ukrainian', query)
        keyword_stmt = select(ProjectChunk).where(
          ProjectChunk.search_vector.op('@@')(ts_query)
        ).order_by(
          func.ts_rank_cd(ProjectChunk.search_vector, ts_query).desc()
        ).limit(50)

        if scope == "project" and project_id:
          keyword_stmt = keyword_stmt.where(ProjectChunk.project_id == project_id)
        elif scope == "system":
          keyword_stmt = keyword_stmt.where(ProjectChunk.project_id == "SYSTEM_REGULATIONS")
        elif scope == "all" and project_id:
          keyword_stmt = keyword_stmt.where(or_(
            ProjectChunk.project_id == project_id,
            ProjectChunk.project_id == "SYSTEM_REGULATIONS"
          ))
        key_res = (await session.execute(keyword_stmt)).scalars().all()

        for chunk in key_res:
          chunk.score = 0.7

      if search_mode == "vector":
        final_docs = vec_res[:limit]
      elif search_mode == "keyword":
        final_docs = key_res[:limit]
      else:
        # HybridRetriever for RRF
        final_docs = await self.retriever.rrf_merge(vec_res, key_res)
        final_docs = final_docs[:limit]

      return [{"id": str(c.id), "content": c.content, "source": c.project_id, "score": getattr(c, "score", 0.0)} for c in final_docs]

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