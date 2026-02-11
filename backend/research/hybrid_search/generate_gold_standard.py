import asyncio
import json
import os
from sqlalchemy import select, func
from app.core.rag_logic import rag_engine, ProjectChunk
from app.core.logger import logger

SEARCH_MAPPING = [
    {
      "query": "Які вимоги до Базового профілю безпеки інформації згідно з НД ТЗІ?",
      "keyword": "НД ТЗІ 3.6-006-24",
      "description": "Пошук за конкретним нормативним документом"
    },
    {
      "query": "Постанова КМУ № 205 від 21 лютого 2025 року",
      "keyword": "Постанова 205",
      "description": "Пошук за точним номером постанови"
    },
    {
      "query": "Які версії PHP підтримує Система після модернізації?",
      "keyword": "PHP 8.3",
      "description": "Технічна вимога щодо оновлення ПЗ"
    },
    {
      "query": "Автоматичне відображення повідомлення Увага! Дипломат!",
      "keyword": "Увага! Дипломат!",
      "description": "Функціональна вимога щодо контролю дипломатичного імунітету"
    },
    {
      "query": "Який час відгуку системи встановлено для 95% запитів?",
      "keyword": "3 секунди",
      "description": "Нефункціональна вимога до продуктивності"
    },
    {
      "query": "Які вимоги до відмовостійкості та допустимого простою системи?",
      "keyword": "не більше 48 годин на рік для непланових робіт",
      "description": "Нефункціональна вимога щодо доступності системи"
    },
    {
      "query": "Яка роль відповідає за управління політиками інформаційної безпеки?",
      "keyword": "Адміністратори безпеки",
      "description": "Вимоги до розподілу ролей та прав доступу"
    },
    {
      "query": "Які вимоги до об'єктного сховища для неструктурованих даних?",
      "keyword": "Шифрування AES-256-GCM, SSL/TLS",
      "description": "Технічні характеристики об'єктного сховища"
    },
    {
      "query": "Який порядок взаємодії з виконавчою службою (ДВС)?",
      "keyword": "автоматичного визначення уповноваженого підрозділу ДВС",
      "description": "Опис бізнес-процесу (BP-6)"
    },
    {
      "query": "Вимоги до клієнтських робочих станцій та оперативної пам'яті",
      "keyword": "Рекомендовані вимоги: 8 GB та вище",
      "description": "Апаратні вимоги до пристроїв користувачів"
    }
]

async def generate_json():
  gold_standard = []
  logger.info("Starting Gold Standard dataset generation with Ranking optimization...")

  async with rag_engine.async_session() as session:
    for item in SEARCH_MAPPING:
      valid_ids = []

      res_ilike = await session.execute(
        select(ProjectChunk.id).where(ProjectChunk.content.ilike(f"%{item['keyword']}%")).limit(3)
      )
      valid_ids.extend(res_ilike.scalars().all())
      
      ts_query = func.websearch_to_tsquery('ukrainian', item['keyword'])
      res_ts = await session.execute(
        select(ProjectChunk.id)
        .where(ProjectChunk.search_vector.op('@@')(ts_query))
        .order_by(func.ts_rank_cd(ProjectChunk.search_vector, ts_query).desc())
          .limit(3)
      )
      valid_ids.extend(res_ts.scalars().all())

      unique_ids = list(set(str(vid) for vid in valid_ids))

      if unique_ids:
          gold_standard.append({
              "query": item["query"],
              "expected_ids": unique_ids,
              "description": item["description"]
          })
          logger.info(f"Mapped query '{item['query'][:30]}...' to {len(unique_ids)} IDs")
      else:
          logger.warning(f"MATCH NOT FOUND for keyword: '{item['keyword']}'")

  output_file = "research/data/gold_standard.json"
  os.makedirs("research/data", exist_ok=True)
  with open(output_file, "w", encoding="utf-8") as f:
    json.dump(gold_standard, f, ensure_ascii=False, indent=2)
  
  logger.info(f"File {output_file} generated. Total valid records: {len(gold_standard)}")

if __name__ == "__main__":
    asyncio.run(generate_json())