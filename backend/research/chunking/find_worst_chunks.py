import asyncio
from sqlalchemy import select
from app.core.rag_logic import rag_engine, ProjectChunk
from research.chunking.semantic_analyzer import SemanticAnalyzer
from app.core.logger import logger

async def find_outliers():
    analyzer = SemanticAnalyzer()
    results = []

    logger.info("Fetching all chunks for error analysis...")
    async with rag_engine.async_session() as session:
        stmt = select(ProjectChunk.project_id, ProjectChunk.content)
        db_result = await session.execute(stmt)
        chunks = db_result.all()

    for project_id, content in chunks:
        stats = analyzer.calculate_variance(content)
        if stats["count"] >= 2:
            results.append({
                "project_id": project_id,
                "variance": stats["variance"],
                "content": content
            })

    # Sort by variance in descending order and take top 3
    worst_chunks = sorted(results, key=lambda x: x['variance'], reverse=True)[:3]

    print("\n" + "="*50)
    print("TOP 3 WORST CHUNKS (Highest Semantic Variance)")
    print("="*50)
    for i, item in enumerate(worst_chunks, 1):
        print(f"\nRANK {i} | Project: {item['project_id']} | Variance: {item['variance']:.5f}")
        print(f"Content Preview: {item['content'][:300]}...")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(find_outliers())