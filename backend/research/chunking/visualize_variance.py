import asyncio
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sqlalchemy import select
from app.core.rag_logic import rag_engine, ProjectChunk
from research.chunking.semantic_analyzer import SemanticAnalyzer
import logging
from app.core.logger import logger

async def generate_research_report():
  analyzer = SemanticAnalyzer()
  variance_results = []

  logger.info("Connecting to pgvector to fetch project chunks...")
  async with rag_engine.async_session() as session:
    # Retrieve chunks stored in the database
    stmt = select(ProjectChunk.content).limit(200)
    result = await session.execute(stmt)
    db_chunks = result.scalars().all()

  if not db_chunks:
    logger.error("No data found in database. Please run your ingestion pipeline first.")
    return

  logger.info(f"Analyzing {len(db_chunks)} chunks from the database...")
  for content in db_chunks:
    stats = analyzer.calculate_variance(content)
    if stats["count"] >= 2:
      variance_results.append(stats["variance"])

  if not variance_results:
    logger.warning("No multi-sentence chunks found to process.")
    return

  # Generating the Boxplot for the thesis documentation
  plt.figure(figsize=(10, 6))
  sns.set_style("whitegrid")
  sns.boxplot(x=variance_results, color="#457B9D")
  
  plt.title('Розподіл семантичної дисперсії', fontsize=14)
  plt.xlabel('Показник дисперсії', fontsize=12)

  plt.grid(axis='x', linestyle='--', alpha=0.7)
  plt.xticks(np.arange(0, 0.035, 0.005))
  
  # Save output to the research folder
  output_file = "research/results/variance_results.png"
  plt.savefig(output_file, dpi=300)
  logger.info(f"Report successfully generated: {output_file}")

if __name__ == "__main__":
  asyncio.run(generate_research_report())