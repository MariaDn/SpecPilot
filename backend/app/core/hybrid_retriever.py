import numpy as np

class HybridRetriever:
  def __init__(self, k_constant=10, vector_weight=0.2):
    self.k = k_constant
    self.vector_weight = vector_weight

  # Reciprocal Rank Fusion
  async def rrf_merge(self, vector_results, keyword_results):
    scores = {}
    
    # Resuts with vector search
    for rank, doc in enumerate(vector_results, start=1):
      doc_id = str(doc.id)
      scores[doc_id] = {
        'doc': doc, 
        'score': (1 / (self.k + rank)) * self.vector_weight
      }
        
    # Resuts with text search
    for rank, doc in enumerate(keyword_results, start=1):
      doc_id = str(doc.id)
      if doc_id in scores:
        scores[doc_id]['score'] += 1 / (self.k + rank)
      else:
        scores[doc_id] = {'doc': doc, 'score': 1 / (self.k + rank)}
    
    # Sorting after RRF score
    sorted_res = sorted(scores.values(), key=lambda x: x['score'], reverse=True)
    return [item['doc'] for item in sorted_res]