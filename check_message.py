import requests
import json
from typing import Dict, Any

from config import openrouter_api_key, app_name, model, filter_short_messages_cnt


def make_request(prompt: str) -> Dict[str, Any]:
    response = requests.post(
      url="https://openrouter.ai/api/v1/chat/completions",
      headers={
        "Authorization": f"Bearer {openrouter_api_key}",
        "HTTP-Referer": app_name, # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": app_name, # Optional. Site title for rankings on openrouter.ai.
      },
      data=json.dumps({
        "model": model,
        "messages": [
          {
            "role": "user",
            "content": prompt,
          }
        ],
        "max_tokens": 1000,
      })
    )

    res = response.json()
    return res


def filter_euristics(text: str) -> bool:
    if len(text) < filter_short_messages_cnt:
        return False
    if 'тебя заблокировали' in text.lower():
        return False
    if '[Нет текста]' == text.strip():
        return False
    if 'spam' in text:
        return False
    if 'deleted' in text:
        return False
    if 'removed' in text:
        return False
    if 'blocked' in text:
        return False
    if 'message' in text:
        return False
    if 'ban' in text:
        return False
    if 'user' in text:
        return False
    if 'kicked' in text:
        return False
    if 'спам' in text:
        return False
    if 'блокировка' in text:
        return False

    return True


def filter_is_nlp_offer(text: str) -> Dict[str, Any]:
    if not filter_euristics(text):
        return {'summary': text, 'keywords': '', 'offer_details': '', 'is_ml_offer': False}

    prompt = f"""Тебе на вход дается сообщение <message>. Это сообщение в социальной сети. 
Тебе надо проанализировать данное сообщение и определить является ли это сообщение запросом на поиск подрядчика или оказание услуг или поиск работника в сфере NLP, Data Science, машинного обучения, внедрения искусственного интеллекта.
Результат анализа нужно записать в виде json следующего формата:
summary: str - краткое саммари сообщения
keywords: str - ключевые слова, которые есть в сообщении, разделенные запятой
offer_details: str - описание запроса, если это запрос на поиск подрядчика или оказание услуг, иначе пустая строка
is_ml_offer: bool - основываясь на выделенной в полях offer_details и summary информации определи, является ли сообщение запросом на поиск подрядчика или оказание услуг в сфере NLP, Data Science, машинного обучения, внедрения искусственного интеллекта, то true, если нет, то false
Если это просто сообщение на темы в сфере NLP, Data Science, машинного обучения, внедрения искусственного интеллекта, но это не запрос на поиск подрядчика, оказание написавшему услуг или не поиск работника по данной тематике, то выводи в этом поле false!
Если это вакансия для работы в офисе крупной IT компании, например Яндекс, Яндекс Маркет и другие bigtech компании, то выводи в этом поле false!

Выводи только валидный json в формате {{"summary": "...", "keywords": "...", "offer_details": "...", "is_ml_offer": ...}}
Экранируй все символы которые могут быть запрещены в json строке, например переносы строк, кавычки, слэш, табуляции и т.д.

<message>{text}</message>

Выведи только результат валидного json и ничего больше!"""

    resp = make_request(prompt)
    res = resp['choices'][0]['message']['content']
    res = res.replace('```json', '')
    res = res.replace('```', '')
    try:
        data = json.loads(res)
    except:
        data = {}
    return data


if __name__ == '__main__':
    text = """Ищем людей или команды, которые могут создавать простых ИИ-агентов для автоматизации бизнес процессов в отдельно взятой отрасли!

Добрый день! Мы - сеть медицинских клиник, а еще - преданные читатели этого канала. И вот складывается ощущение, что в канале - 2025 год, а у нас в отрасли - пахнет дореволюционным нафталином. Столько ИИшных возможностей хочется реализовать на практике, но совершенно не получается, потому что:

- отраслевые информационные системы дремучие, часто не имеют API или имеют, но скудный и плохой;
 ⁃ очень мало умельцев, которые одновременно ориентируются и во всем зоопарке ИИ моделей, и в том, как их пришить к действующим ИТ системам в организации (RPA, Silenium, может что-то еще)

Хотим местные захватывающие дух «сказки» сделать действующей и помогающей людям былью и ищем подрядчиков - разбирающихся в вопросе ребят или команды.

Пишите сюда, (https://t.me/ibi2104) будем рады познакомиться!

#промо"""

    res = filter_is_nlp_offer(text)
    print(res)
