import asyncio
import json
import os
import re
import httpx
import time
from datetime import datetime
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("AI_API_KEY")
JUDGE_MODEL_ID = "google/gemma-2-9b-it" 
API_URL = "http://127.0.0.1:8000/api/generate"

judge_client = InferenceClient(model=JUDGE_MODEL_ID, token=HF_TOKEN)

TEST_DATASET = [
  "Яка повна назва проєкту модернізації?",
  "Скільки етапів передбачено Планом-графіком виконання робіт?",
  "Які трудові витрати заплановані на Етап ІІ (Доопрацювання підсистем)?",
  "Які вимоги до операційної системи серверів?",
  "Які мінімальні вимоги до оперативної пам'яті для клієнтських робочих станцій?",
  "Який час відгуку системи встановлено для 95% запитів?",
  "Який рівень доступності системи вимагається?",
  "З яких логічних рівнів повинна складатися архітектура системи?",
  "Що має бути реалізовано в рамках функціональної вимоги FR-1.1 щодо взаємодії з поштовим оператором?",
  "Які вимоги до Базового профілю безпеки інформації згідно з НД ТЗІ?",
  "Постанова КМУ № 205 від 21 лютого 2025 року - про що вона?",
  "Які версії PHP підтримує Система після модернізації?",
  "Який час відгуку системи встановлено для 95% запитів?",
  "Які вимоги до клієнтських робочих станцій та оперативної пам'яті?",
  "Яка роль відповідає за управління політиками інформаційної безпеки?"
]

NAVIGATION_JUDGE_PROMPT = """
Ти — аудитор RAG-системи. Твоє завдання — перевірити, чи базується відповідь Асистента ВИКЛЮЧНО на наданому контексті.

КОНТЕКСТ:
{context}

ЗАПИТ КОРИСТУВАЧА:
{question}

ВІДПОВІДЬ АСИСТЕНТА:
{answer}

Поверни JSON: {{ "score": 0 або 1, "reasoning": "пояснення українською" }}
"""

async def query_local_rag(question: str):
  payload = {
    "mode": "qa_navigation",
    "messages": [{"role": "user", "content": [{"type": "text", "text": question}]}],
    "context": {
      "questionnaire": {}, "target_sections": ["1"],
      "task_metadata": {"project_id": "gold"}
    }
  }
  async with httpx.AsyncClient(timeout=60.0) as client:
    try:
      resp = await client.post(API_URL, json=payload)
      if resp.status_code != 200: return None, None
      data = resp.json()
      output = data.get("output", {})
      answer = output.get("answer") or output.get("content") or str(output)
      context = output.get("diagnostics", {}).get("thought_process") or data.get("rag_context") or ""
      return answer, str(context)
    except Exception: return None, None

async def run_comprehensive_test():
  print(f"Запуск Faithfulness Test: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
  report = []
  
  for i, q in enumerate(TEST_DATASET):
    print(f"\n[{i+1}/{len(TEST_DATASET)}] Запит: {q}")
    answer, context = await query_local_rag(q)
    
    if not answer:
      print("Помилка API")
      continue

    messages = [
      {"role": "system", "content": "Ти — аудитор. Відповідай ТІЛЬКИ JSON."},
      {"role": "user", "content": NAVIGATION_JUDGE_PROMPT.format(context=context, question=q, answer=answer)}
    ]

    try:
      response_obj = judge_client.chat_completion(messages=messages, max_tokens=500, temperature=0.1)
      raw_eval = response_obj.choices[0].message.content
      match = re.search(r"\{.*\}", raw_eval, re.DOTALL)
      eval_data = json.loads(match.group()) if match else {"score": 0, "reasoning": "Парсинг JSON провалено"}
      
      score = eval_data.get("score", 0)
      status = "PASS" if score == 1 else "🚨 HALLUCINATION"
      print(f"{status} | Оцінка: {score}")
      print(f"Чому: {eval_data.get('reasoning')}")
      
      report.append({"question": q, "score": score, "reason": eval_data.get('reasoning'), "answer": answer})
    except Exception as e:
      print(f"Суддя не зміг відповісти: {e}")

  if report:
    accuracy = (sum(r['score'] for r in report) / len(report)) * 100
    print(f"\n{'='*40}\nПІДСУМОК: {accuracy:.2f}% Faithfulness\n{'='*40}")
    
    filename = f"test_report_{int(time.time())}.json"
    with open(filename, "w", encoding="utf-8") as f:
      json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Звіт збережено у: {filename}")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())