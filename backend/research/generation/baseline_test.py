import asyncio
import json
import os
from typing import Dict, Any
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("AI_API_KEY")
MODEL_ID = "google/gemma-2-9b-it"

client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

BASELINE_SYSTEM_PROMPT = """
Ти — технічний асистент. Твоє завдання — написати Технічне завдання (ТЗ) для IT-проєкту на основі наданих даних.
ТЗ має відповідати українським стандартам.
"""

async def generate_baseline_tz(questionnaire: Dict[str, Any], output_file: str):
  print(f"--- Запуск Baseline генерації в {output_file} ---")
  
  q_text = json.dumps(questionnaire, ensure_ascii=False, indent=2)
  
  user_message = f"""
  Ось дані про проєкт:
  {q_text}
  
  Будь ласка, згенеруй повний текст Технічного завдання для цього проєкту.
  """
  
  messages = [
    {"role": "system", "content": BASELINE_SYSTEM_PROMPT},
    {"role": "user", "content": user_message}
  ]
  
  try:
    response = client.chat_completion(
      messages=messages,
      max_tokens=4000,
      temperature=0.7
    )
    
    content = response.choices[0].message.content
    
    with open(output_file, "w", encoding="utf-8") as f:
      f.write(content)
        
    return content
      
  except Exception as e:
    return None

if __name__ == "__main__":
  try:
    with open("research/data/questionnaire_sample.json", "r", encoding="utf-8") as f:
      sample_data = json.load(f)
    
    asyncio.run(generate_baseline_tz(sample_data, "research/data/baseline_output_1.md"))
  except FileNotFoundError:
