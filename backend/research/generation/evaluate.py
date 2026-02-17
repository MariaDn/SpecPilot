import os
import json
import re
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("AI_API_KEY")
JUDGE_MODEL_ID = "google/gemma-2-9b-it"

client = InferenceClient(model=JUDGE_MODEL_ID, token=HF_TOKEN)

def calculate_deterministic_scores(text: str) -> dict:
  """
  Python рахує бали за структуру, факти та СТИЛЬ на основі словників.
  """
  scores = {
    "structural_score": 0,
    "factual_score": 0,
    "style_score": 0, 
    "missing_items": []
  }
  
  header_pattern = r"(##\s*)?1\.\s*Загальні відомості"
  if re.search(header_pattern, text[:1000], re.IGNORECASE):
    scores["structural_score"] = 40
  else:
    scores["missing_items"].append("Неправильний заголовок (має бути '1. Загальні відомості')")

  if "205" in text and ("Постанова" in text or "постанова" in text):
    scores["factual_score"] += 20
  else:
    scores["missing_items"].append("Відсутнє посилання на Постанову №205")

  if "3008" in text:
    scores["factual_score"] += 20
  else:
    scores["missing_items"].append("Відсутнє посилання на ДСТУ 3008")

  official_markers = [
    r"має бути",           # Імператив
    r"повин(ен|на|но|ні)", # Зобов'язання
    r"забезпеч(увати|ити)",# Функціональність
    r"здійснювати",        # Дія
    r"відповідно до",      # Посилання на норми
    r"згідно з",           # Посилання на норми
    r"на підставі",        # Юридична підстава
    r"з метою",            # Цілепокладання
    r"в частині",          # Уточнення
    r"передбача(ти|ється)" # Проєктування
  ]

  bad_markers = [
    r"\bя\b", r"\bми\b",   # Займенники 1 особи (недопустимі в ТЗ)
    r"думаю", r"напевно",  # Невпевненість
    r"швидко", r"гарно",   # Суб'єктивні прикметники (має бути "200 мс", "зручний інтерфейс")
    r"супер", r"клас"      # Сленг
  ]

  found_official = 0
  for marker in official_markers:
    if re.search(marker, text, re.IGNORECASE):
      found_official += 1
  
  found_bad = 0
  bad_words_found = []
  for marker in bad_markers:
    found = re.search(marker, text, re.IGNORECASE)
    if found:
      found_bad += 1
      bad_words_found.append(found.group(0))

  if found_official >= 6:
    scores["style_score"] = 20
  elif found_official >= 3:
    scores["style_score"] = 10
    scores["missing_items"].append(f"Слабкий офіційний стиль (знайдено лише {found_official} маркерів)")
  else:
    scores["style_score"] = 0
    scores["missing_items"].append("Текст не схожий на офіційний документ")

  if found_bad > 0:
    scores["style_score"] = max(0, scores["style_score"] - (found_bad * 5))
    scores["missing_items"].append(f"Знайдено недопустимі слова: {', '.join(bad_words_found)}")

  scores["total_score"] = scores["structural_score"] + scores["factual_score"] + scores["style_score"]
  
  return scores

def generate_reasoning(text_sample: str, scores: dict) -> str:
  """LLM пояснює, чому такі бали, формуючи висновок"""
  
  missing_str = ", ".join(scores["missing_items"]) if scores["missing_items"] else "Зауважень немає."
  
  prompt = f"""
  Ти — технічний аудитор. Тобі дали результати автоматичної перевірки ТЗ.
  
  РЕЗУЛЬТАТИ ПЕРЕВІРКИ:
  - Структура: {scores['structural_score']}/40
  - Фактологія: {scores['factual_score']}/40
  - Стиль: {scores['style_score']}/20
  - ЗНАЙДЕНІ ПОМИЛКИ: {missing_str}
  
  Твоє завдання: Напиши КОРОТКИЙ висновок (Reasoning) українською мовою.
  Поясни, чому оцінка саме така, опираючись на список помилок.
  
  Приклад висновку: "Структура документа порушена, оскільки перший розділ названо неправильно. Також відсутні обов'язкові посилання на..."
  """
  
  try:
    response = client.chat_completion(
      messages=[{"role": "user", "content": prompt}],
      max_tokens=200,
      temperature=0.7
    )
    return response.choices[0].message.content.strip()
  except Exception:
    return f"Автоматичний висновок: Виявлено помилки: {missing_str}"

def run_comparison(enhanced_file: str, baseline_file: str, questionnaire_file: str):
  try:
    with open(enhanced_file, "r", encoding="utf-8") as f:
      enhanced_text = f.read()
    with open(baseline_file, "r", encoding="utf-8") as f:
      baseline_text = f.read()
  except FileNotFoundError as e:
    print(f"Не знайдено файл: {e.filename}")
    return

  print("Обробка Baseline...")
  base_scores = calculate_deterministic_scores(baseline_text)
  base_reasoning = generate_reasoning(baseline_text, base_scores)
  
  print("Обробка Enhanced...")
  enh_scores = calculate_deterministic_scores(enhanced_text)
  enh_reasoning = generate_reasoning(enhanced_text, enh_scores)
  
  print("\n" + "="*45)
  print(" РЕЗУЛЬТАТИ ГІБРИДНОГО ОЦІНЮВАННЯ")
  print("="*45)
  print(f"{'Metric':<20} | {'Baseline':<10} | {'Enhanced':<10}")
  print("-" * 45)
  print(f"{'Structure':<20} | {base_scores['structural_score']:<10} | {enh_scores['structural_score']:<10}")
  print(f"{'Factuality':<20} | {base_scores['factual_score']:<10} | {enh_scores['factual_score']:<10}")
  print(f"{'Style':<20} | {base_scores['style_score']:<10} | {enh_scores['style_score']:<10}")
  print("-" * 45)
  print(f"{'TOTAL SCORE':<20} | {base_scores['total_score']:<10} | {enh_scores['total_score']:<10}")
  print("="*45)
  
  print(f"\n📝 Baseline Verdict:\n{base_reasoning}")
  print(f"\n📝 Enhanced Verdict:\n{enh_reasoning}")

if __name__ == "__main__":
  ENHANCED_PATH = "research/data/enhanced_output.md"
  BASELINE_PATH = "research/data/baseline_output_1.md"
  QUESTIONNAIRE_PATH = "research/data/questionnaire_sample.json"
  
  if not os.path.exists(ENHANCED_PATH):
    ENHANCED_PATH = "enhanced_output.md"
    BASELINE_PATH = "baseline_output_1.md"
    QUESTIONNAIRE_PATH = "questionnaire_sample.json"

  run_comparison(ENHANCED_PATH, BASELINE_PATH, QUESTIONNAIRE_PATH)