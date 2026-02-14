import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_json(text: str) -> str:
    text = text.strip()
    if "```json" in text:
        return text.split("```json")[1].split("```")[0].strip()
    if "{" in text:
        return text[text.find("{"):text.rfind("}") + 1]
    return text

def parse_to_output(mode: str, text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        if mode == "generate_tz":
            return {"document": {"sections": []}, "raw_text": text}
        return {"answer": {"text": text, "citations": []}}

def run_tests():
    print("Запуск тестів логіки Handler...")

    perfect_json = '{"document": {"sections": [{"code": "1", "name": "Вступ"}]}}'
    assert parse_to_output("generate_tz", extract_json(perfect_json))['document']['sections'][0]['code'] == "1"
    print("Кейс 1: Ідеальний JSON - ОК")

    markdown_json = """
    Ось ваше ТЗ:
    ```json
    {
        "document": {
            "sections": [{"code": "2", "name": "Вимоги"}]
        }
    }
    ```
    Сподіваюсь, це допоможе.
    """
    cleaned = extract_json(markdown_json)
    parsed = parse_to_output("generate_tz", cleaned)
    assert parsed['document']['sections'][0]['code'] == "2"
    print("Кейс 2: JSON у Markdown - ОК")

    text_json = """
    Звісно, ось дані:
    { "document": { "sections": [] } }
    """
    cleaned = extract_json(text_json)
    assert "document" in parse_to_output("generate_tz", cleaned)
    print("Кейс 3: Текст із дужками - ОК")

    broken_json = '{ "document": { "sections": ... помилка ... }'
    result = parse_to_output("generate_tz", extract_json(broken_json))
    assert "raw_text" in result
    print("Кейс 4: Обробка помилок (Fallback) - ОК")

    print("\nВсі тести пройдено успішно! Логіка парсингу готова до деплою.")

if __name__ == "__main__":
    run_tests()