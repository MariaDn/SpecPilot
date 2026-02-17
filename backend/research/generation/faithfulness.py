import os
import json
import re
import asyncio
import httpx
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("AI_API_KEY")
JUDGE_MODEL_ID = "google/gemma-2-9b-it"

client = InferenceClient(model=JUDGE_MODEL_ID, token=HF_TOKEN)

FAITHFULNESS_PROMPT = """
Ти — суворий технічний контролер. Твоє завдання — перевірити ВІРНІСТЬ (Faithfulness) згенерованого тексту відносно вхідних даних.
Перевір, чи не містить згенерований текст "галюцинацій" (вигаданих фактів, яких немає в анкеті).

ВХІДНІ ДАНІ ПРОЄКТУ (JSON):
{context}

ЗГЕНЕРОВАНИЙ РОЗДІЛ ТЗ:
{answer}

ТВОЄ ЗАВДАННЯ:
1. Виділи ключові технічні факти у тексті (назви, стек технологій, терміни, вимоги).
2. Перевір, чи кожен факт підтверджується вхідними даними.
3. Якщо в анкеті вказано "PostgreSQL", а в тексті "MySQL" — це помилка вірності.

ОЦІНКА (0.0 - 1.0):
Розрахуй як: (Кількість підтверджених фактів) / (Загальна кількість фактів у тексті).

Поверни результат у форматі JSON:
{{
  "score": 0.00,
  "reasoning": "коротке пояснення"
}}
"""

async def evaluate_faithfulness(questionnaire_path: str, output_path: str):
  try:
    with open(questionnaire_path, "r", encoding="utf-8") as f:
      q_data = json.load(f)
    with open(output_path, "r", encoding="utf-8") as f:
      generated_text = f.read()
  except FileNotFoundError as e:
    print(f"Помилка: Файл не знайдено - {e.filename}")
    return

  print(f"Тестування Faithfulness для: {output_path}")

  context_str = json.dumps(q_data, ensure_ascii=False, indent=2)[:2500]
  answer_str = generated_text[:3500]

  prompt = FAITHFULNESS_PROMPT.format(context=context_str, answer=answer_str)

  try:
    response = client.chat.completions.create(
      messages=[{"role": "user", "content": prompt}],
      max_tokens=600,
      temperature=0.1
    )
    
    raw_content = response.choices[0].message.content
    
    match = re.search(r"\{.*\}", raw_content, re.DOTALL)
    if match:
      json_str = match.group(0)
      result = json.loads(json_str, strict=False)
      
      print(f"\nРезультат тесту:")
      print(f"   Score: {result.get('score', 0) * 100}%")
      print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
      return result
    else:
      print(f"Не вдалося знайти JSON у відповіді. Сирий текст:\n{raw_content}")

  except Exception as e:
    print(f"Критична помилка при оцінюванні: {str(e)}")

if __name__ == "__main__":
  Q_PATH = "research/data/questionnaire_sample.json"
  OUT_PATH = "research/data/enhanced_output.md"
  
  if not os.path.exists(Q_PATH):
    Q_PATH = "questionnaire_sample.json"
    OUT_PATH = "enhanced_output.md"

  asyncio.run(evaluate_faithfulness(Q_PATH, OUT_PATH))