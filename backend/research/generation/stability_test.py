import asyncio
import time
import json
import os
import statistics
import httpx
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("AI_API_KEY")
JUDGE_MODEL_ID = "google/gemma-2-9b-it" 
BASELINE_MODEL_ID = "google/gemma-2-9b-it"

API_URL = "http://127.0.0.1:8000/api/generate"

client = InferenceClient(token=HF_TOKEN)

STRICT_JUDGE_PROMPT = """
Ти — суворий аудитор документації. Твоє завдання — перевірити СТАБІЛЬНІСТЬ роботи системи.
Порівняй два тексти (Run A та Run B) і оціни їхню структурну та змістовну тотожність.

ТЕКСТ A:
{text1}

ТЕКСТ B:
{text2}

КРИТЕРІЇ ОЦІНКИ (0-100):
1. **Ідентичність заголовків (40 балів):** Чи збігаються назви розділів та їх нумерація літера-в-літеру?
  - Якщо в А "3.1 Вимоги", а в B "3. Функціональні вимоги" -> ШТРАФ -20.
2. **Формат даних (30 балів):**
  - Якщо в А таблиця, а в B список -> ШТРАФ -30 (0 балів за цей пункт).
  - Якщо в А коди вимог "FR-1", а в B "Вимога 1" -> ШТРАФ -30.
3. **Контент (30 балів):**
  - Чи однаковий стек технологій і ключові параметри (наприклад, CPU/RAM)?

ШКАЛА:
- 100: Тексти ідентичні (допускаються незначні зміни слів-зв'язок).
- 80-90: Структура однакова, але є різні формулювання в описі.
- 50-70: Структура схожа, але різні заголовки або деталі.
- < 50: Різні формати (таблиця vs текст) або різний зміст.

Поверни ТІЛЬКИ ЦИФРУ від 0 до 100.
"""

async def generate_baseline(q_json: dict) -> str:
  
  prompt = f"""
  Напиши розділ "Функціональні вимоги" для IT-системи.
  Ось вхідні дані: {json.dumps(q_json, ensure_ascii=False)}
  
  Вимоги:
  1. Опиши функціонал.
  2. Додай таблицю.
  3. Вкажи технічні деталі.
  """
  try:
    response = client.chat_completion(
      model=BASELINE_MODEL_ID,
      messages=[{"role": "user", "content": prompt}],
      max_tokens=2000,
      temperature=0.9
    )
    return response.choices[0].message.content
  except Exception as e:
    print(f"Error Baseline: {e}")
    return ""

async def generate_enhanced(q_json: dict) -> str:

  payload = {
    "mode": "generate_tz",
    "messages": [],
    "context": {
      "questionnaire": q_json,
      "target_sections": ["3"]
    }
  }
    
  print(f"[DEBUG] Sending to {API_URL}...")
  
  async with httpx.AsyncClient(timeout=600.0) as http_client:
    try:
      resp = await http_client.post(API_URL, json=payload)
      
      if resp.status_code != 200:
        print(f"API Error {resp.status_code}: {resp.text}")
        return ""
          
      data = resp.json()
      
      if "status" in data and data["status"] == "error":
        print(f"Backend Error: {data.get('message', 'Unknown error')}")
        return ""

      if 'output' in data and 'document' in data['output']:
        sections = data['output']['document']['sections']
        content_list = [s['content'] for s in sections if s.get('content')]
        
        full_text = "\n".join(content_list)

        if len(full_text) < 100:
          print(f"Warning: Текст підозріло короткий ({len(full_text)} chars): '{full_text}'")
          return ""

        return full_text
      else:
        print(f"Неочікувана структура JSON: {data.keys()}")
        return ""
            
    except httpx.ReadTimeout:
      print("   ⏳ Таймаут (сервер думав надто довго).")
      return ""
    except Exception as e:
      print(f"Critical Error: {e}")
      return ""

def calculate_stability(responses: list) -> float:
  if len(responses) < 2: return 0.0, 0.0
  
  scores = []
  print("Суддя (Strict Mode) порівнює прогони...")
  
  for i in range(len(responses) - 1):
    text1 = responses[i][:4000]
    text2 = responses[i+1][:4000]
    
    prompt = STRICT_JUDGE_PROMPT.format(text1=text1, text2=text2)
    
    try:
      res = client.chat_completion(
        model=JUDGE_MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0.0
      )
      score_str = ''.join(filter(str.isdigit, res.choices[0].message.content))
      score = int(score_str)
      scores.append(score)
      print(f"      Pair {i+1}-{i+2}: {score}/100")
    except:
      scores.append(50)

  mean_val = statistics.mean(scores)
  stdev_val = statistics.stdev(scores) if len(scores) > 1 else 0.0
  
  return mean_val, stdev_val

async def main():
  try:
    with open("research/data/questionnaire_sample.json", "r", encoding="utf-8") as f:
      q_data = json.load(f)
  except:
    print("Немає файлу questionnaire_sample.json. Використовую заглушку.")
    q_data = {"project_info": {"basic_data": {"full_name": "Test System"}}}

  N_RUNS = 3

  print(f"\nТЕСТ СТАБІЛЬНОСТІ (N={N_RUNS})\n")

  print("1️Генерація Baseline (Zero-shot)...")
  base_resps = []
  for i in range(N_RUNS):
    print(f"   Run {i+1}...")
    txt = await generate_baseline(q_data)
    base_resps.append(txt)
  
  base_mean, base_std = calculate_stability(base_resps)
  print(f">>> Baseline: {base_mean:.1f}% ±{base_std:.1f}")

  print("\n2️Генерація Enhanced...")
  enh_resps = []
  for i in range(N_RUNS):
    print(f"   Run {i+1}...")
    txt = await generate_enhanced(q_data)
    if txt:
      print(f"OK ({len(txt)} chars)")
      enh_resps.append(txt)
    else:
      print("FAILED")
        
    print("Cooling down (15s)...")
    time.sleep(15)
  
  enh_mean, enh_std = calculate_stability(enh_resps)
  print(f">>> Enhanced: {enh_mean:.1f}% ±{enh_std:.1f}")

  print("\n" + "="*50)
  print(f"{'System':<15} | {'Stability (Mean)':<18} | {'Std Dev (Variance)':<15}")
  print("-" * 50)
  print(f"{'Baseline':<15} | {base_mean:.1f}%{'':<12} | ±{base_std:.1f}")
  print(f"{'Enhanced':<15} | {enh_mean:.1f}%{'':<12} | ±{enh_std:.1f}")
  print("="*50)

if __name__ == "__main__":
    asyncio.run(main())