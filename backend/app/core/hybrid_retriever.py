import numpy as np

class HybridRetriever:
  def __init__(self, k_constant=60):
    self.k = k_constant

  # Reciprocal Rank Fusion
  async def rrf_merge(self, vector_results, keyword_results):
    scores = {}
    
    # Resuts with vector search
    for rank, doc in enumerate(vector_results, start=1):
      scores[doc.id] = {'doc': doc, 'score': 1 / (self.k + rank)}
        
    # Resuts with text search
    for rank, doc in enumerate(keyword_results, start=1):
      if doc.id in scores:
        scores[doc.id]['score'] += 1 / (self.k + rank)
      else:
        scores[doc.id] = {'doc': doc, 'score': 1 / (self.k + rank)}
    
    # Sorting after RRF score
    sorted_res = sorted(scores.values(), key=lambda x: x['score'], reverse=True)
    return [item['doc'] for item in sorted_res]