import asyncio
import json
import os
from app.core.rag_logic import rag_engine
from app.core.logger import logger

class BenchmarkRunner:
  def __init__(self, data_path: str):
    self.data_path = data_path
    if not os.path.exists(data_path):
      raise FileNotFoundError(f"Dataset not found at {data_path}. Please run generate_gold_standard.py first.")
    self.test_cases = self._load_data()

  def _load_data(self):
    with open(self.data_path, 'r', encoding='utf-8') as f:
      return json.load(f)

  async def run(self):
    results = {
      "vector": {"mrr": 0.0, "hits": 0},
      "keyword": {"mrr": 0.0, "hits": 0},
      "hybrid": {"mrr": 0.0, "hits": 0}
    }
    
    total = len(self.test_cases)
    logger.info(f"Starting performance benchmark for {total} test cases...")

    for case in self.test_cases:
      query = case["query"]
      expected_ids = [str(eid) for eid in case["expected_ids"]]
      
      for mode in ["vector", "keyword", "hybrid"]:
        retrieved_chunks = await rag_engine.get_context(query=query, search_mode=mode, limit=5)
        retrieved_ids = [str(r["id"]) for r in retrieved_chunks]

        hit_index = next((i for i, rid in enumerate(retrieved_ids) if rid in expected_ids), None)
        
        if hit_index is not None:
          results[mode]["hits"] += 1
          results[mode]["mrr"] += 1.0 / (hit_index + 1)
        else:
          top_got = retrieved_chunks[0]["content"][:100] if retrieved_chunks else "NOTHING FOUND"
          logger.info(f"[{mode.upper()}] Missed: {query}")
          logger.info(f"   - Expected: {expected_ids}")
          logger.info(f"   - Top-1 Found: {top_got}...")

    self._display_final_report(results, total)
    return results

  def _calculate_rank(self, results, expected_id):
    for i, res in enumerate(results):
      if str(res["id"]) == expected_id:
        return i + 1
    return 0

  def _display_final_report(self, results, total):
    print("\n" + "="*50)
    print(f"{'RAG SEARCH PERFORMANCE REPORT':^50}")
    print("="*50)
    print(f"{'Mode':<15} | {'Hit Rate @5':<15} | {'MRR':<10}")
    print("-" * 50)
      
    for mode, data in results.items():
      hit_rate = (data["hits"] / total) * 100
      mrr = data["mrr"] / total
      print(f"{mode.upper():<15} | {hit_rate:>10.1f}%     | {mrr:>8.3f}")
    print("="*50 + "\n")

async def main():
  runner = BenchmarkRunner("research/data/gold_standard.json")
  await runner.run()

if __name__ == "__main__":
    asyncio.run(main())