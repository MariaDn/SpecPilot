import asyncio
import os
from sqlalchemy import select, func
from app.core.rag_logic import RAGEngine, ProjectChunk

async def debug_search(query: str):
  rag = RAGEngine()
  query_vector = rag.embeddings.embed_query(query)
  
  print(f"DEBUG SEARCH: '{query}'")
  print("-" * 60)

  async with rag.async_session() as session:
    dist_col = ProjectChunk.embedding.cosine_distance(query_vector).label("distance")
    
    stmt = select(ProjectChunk, dist_col).order_by("distance").limit(5)
    result = await session.execute(stmt)
    rows = result.all()

    if not rows:
      print("База порожня або результати не знайдено.")
      return

    for i, (chunk, distance) in enumerate(rows, 1):
      similarity = 1 - distance
      print(f"Rank {i} | ID: {chunk.id} | Score (Sim): {similarity:.4f} | Dist: {distance:.4f}")
      print(f"Content: {chunk.content[:150]}...")
      print("-" * 60)

if __name__ == "__main__":
    test_query = "Які версії PHP підтримує Система після модернізації?"
    asyncio.run(debug_search(test_query))