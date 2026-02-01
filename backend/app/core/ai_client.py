import os
import httpx
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

  async def generate_response(self, questionnaire: dict, rag_chunks: list):
    system_instruction = (
      "Ти — професійний Requirements Engineer. "
      "Твоє завдання: згенерувати ТЗ за структурою КМУ №205, використовуючи наданий контекст. "
      "Дані з 'questionnaire' — це прямі відповіді замовника. "
      "Дані з 'rag_chunks' — це нормативні вимоги та зразки. "
      "Якщо в опитувальнику бракує даних для розділу — вкажи це."
    )

    payload = {
      "model": self.model,
      "messages": [
          {"role": "system", "content": system_instruction},
          {
              "role": "user", 
              "content": f"Context Questionnaire: {questionnaire}\n\nRAG Reference Data: {rag_chunks}"
          }
      ],
      "temperature": 0.2
    }

    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
      try:
        response = await client.post(self.api_url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
      except Exception as e:
        return f"Помилка зовнішнього AI: {str(e)}"

ai_client = ExternalAIClient()