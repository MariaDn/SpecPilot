import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

load_dotenv()

class RAGEngine:
  def __init__(self):
    device = "cpu" 
        
    self.embeddings = HuggingFaceEmbeddings(
      model_name="sentence-transformers/all-mpnet-base-v2",
      model_kwargs={'device': device}
    )
    
    self.client = QdrantClient(
      host=os.getenv("QDRANT_HOST", "localhost"),
      port=int(os.getenv("QDRANT_PORT", 6333))
    )
    self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "it_docs")
    self._ensure_collection_exists()
    
    self.vector_store = QdrantVectorStore(
      client=self.client,
      collection_name=self.collection_name,
      embedding=self.embeddings,
    )

  def _ensure_collection_exists(self):
    """Створює колекцію, якщо її немає в Qdrant"""
    collections = self.client.get_collections().collections
    exists = any(c.name == self.collection_name for c in collections)
    
    if not exists:
      self.client.create_collection(
        collection_name=self.collection_name,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
      )
      print(f"Колекція '{self.collection_name}' створена успішно.")

  def ingest_documents(self, directory_path: str):
    """Етап 1: Розбиття на фрагменти та індексація"""
    if not os.path.exists(directory_path):
      return f"Помилка: Папка {directory_path} не знайдена."

    loader = DirectoryLoader(directory_path, glob="**/*.md", loader_cls=TextLoader)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    fragments = text_splitter.split_documents(docs)

    if fragments:
      self.vector_store.add_documents(fragments)
      return f"Успішно проіндексовано {len(fragments)} фрагментів."
    return "Файли не знайдені або порожні."

  def get_context(self, query: str, k: int = 3):
    """Етап 2: Пошук топ-k фрагментів та формування контексту"""
    search_results = self.vector_store.similarity_search(query, k=k)
    
    context_parts = []
    for doc in search_results:
      source = doc.metadata.get('source', 'Unknown')
      context_parts.append(f"[Джерело: {source}]\n{doc.page_content}")
        
    return "\n---\n".join(context_parts)

rag_engine = RAGEngine()