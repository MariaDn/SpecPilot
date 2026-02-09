import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import torch
from app.core.logger import logger

class SemanticAnalyzer:
  def __init__(self, model_name='all-mpnet-base-v2'):
    # Using the same model as in RAG engine
    logger.info(f"Initializing SemanticAnalyzer with model: {model_name}")
    self.model = SentenceTransformer(model_name)

  def calculate_variance(self, chunk_text: str):
    # Split chunk into sentences
    sentences = [s.strip() for s in chunk_text.split('.') if len(s.strip()) > 10]
    if len(sentences) < 2:
      return {
        "variance": 0.0, 
        "mean_similarity": 1.0, 
        "count": len(sentences)
      }

    # 1. Generate embeddings for each sentence
    embeddings = self.model.encode(sentences)

    # 2. Calculate the Centroid (average vector of the chunk)
    centroid = np.mean(embeddings, axis=0).reshape(1, -1)

    # 3. Calculate similarities between each sentence and the centroid
    similarities = cosine_similarity(embeddings, centroid).flatten()

    # 4. Calculate Variance
    # High variance = sentences are topically different
    # Low variance = chunk is semantically focused
    variance = np.var(similarities)
    mean_similarity = np.mean(similarities)

    return {
      "variance": float(variance),
      "mean_similarity": float(mean_similarity),
      "count": len(sentences)
    }
