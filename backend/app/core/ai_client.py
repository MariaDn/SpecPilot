import os
import httpx
from typing import Any
from dotenv import load_dotenv

load_dotenv()

class ExternalAIClient:
  def __init__(self):
    self.api_url = os.getenv("AI_API_URL")
    self.api_key = os.getenv("AI_API_KEY")
    self.model = os.getenv("AI_MODEL_NAME")

  async def check_connection(self):
    payload = {
      "model": self.model,
      "messages": [{"role": "user", "content": "ping"}],
      "max_tokens": 1 
    }
    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=5.0) as client:
      try:
        response = await client.post(self.api_url, json=payload, headers=headers)
        if response.status_code == 200:
          return {"status": "healthy", "message": "Зв'язок з AI встановлено"}
        return {
          "status": "unhealthy", 
          "error": f"API повернув помилку {response.status_code}: {response.text}"
        }
      except Exception as e:
        return {"status": "error", "error": str(e)}

  async def generate_structured_response(self, request_data: Any):
    payload = {
      "model": self.model,
      "mode": request_data.mode,
      "messages": [m.dict() for m in request_data.messages],
      "context": request_data.context.dict(),
      "generation_config": {
        "temperature": 0.2,
        "max_tokens": 2048
      }
    }

    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
      try:
        response = await client.post(self.api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
      except Exception as e:
        return {
          "status": "error",
          "message": f"AI Client Error: {str(e)}"
        }

ai_client = ExternalAIClient()