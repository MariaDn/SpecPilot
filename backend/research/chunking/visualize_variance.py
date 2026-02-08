import asyncio
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import select
from app.core.rag_logic import rag_engine, ProjectChunk
from research.chunking.semantic_analyzer import SemanticAnalyzer
import logging

# English logging for the research script
logger = logging.getLogger("VisualizationTool")
logging.basicConfig(level=logging.INFO)

async def generate_research_report():
  analyzer = SemanticAnalyzer()
  variance_results = []

  logger.info("Connecting to pgvector to fetch real project chunks...")
  async with rag_engine.async_session() as session:
    # Retrieve chunks stored in the database
    stmt = select(ProjectChunk.content).limit(200)
    result = await session.execute(stmt)
    db_chunks = result.scalars().all()

  if not db_chunks:
    logger.error("No data found in database. Please run your ingestion pipeline first.")
    return

  logger.info(f"Analyzing {len(db_chunks)} real chunks from the database...")
  for content in db_chunks:
    stats = analyzer.calculate_variance(content)
    if stats["count"] >= 2:
      variance_results.append(stats["variance"])

  # Generating the Boxplot for the thesis documentation
  plt.figure(figsize=(10, 6))
  sns.set_style("whitegrid")
  sns.boxplot(x=variance_results, color="#457B9D")
  
  plt.title('Semantic Variance Distribution (Real Project Chunks)', fontsize=14)
  plt.xlabel('Variance Score (Lower is better)', fontsize=12)
  
  # Save output to the research folder
  output_file = "research/chunking/variance_results.png"
  plt.savefig(output_file, dpi=300)
  logger.info(f"Report successfully generated: {output_file}")

if __name__ == "__main__":
  asyncio.run(generate_research_report())