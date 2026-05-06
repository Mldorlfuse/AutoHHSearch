import requests
import time

import config

class ServiceAi:
    @staticmethod
    def get_gemini_response(vacancy_text):
        conf = config.AI_STANDARD_SETTINGS
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {conf['api_key']}"
        }
        full_prompt = f"{config.SYSTEM_PROMPT}\n\nВАКАНСИЯ:\n{vacancy_text}"
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": conf["temperature"], "topP": conf["top_p"]}
        }

        for attempt in range(conf["max_retries"]):
            try:
                response = requests.post(conf["url"], headers=headers, json=payload, timeout=60)
                if response.status_code in [429, 503]:
                    time.sleep(10)
                    continue
                response.raise_for_status()
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                print(f"Ошибка API Письма (попытка {attempt + 1}): {e}")
                time.sleep(5)
        return None

    @staticmethod
    def get_gemini_response_for_questions(prompt):
        conf = config.AI_FORM_SETTINGS
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {conf['api_key']}"
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": conf["temperature"], "topP": conf["top_p"]}
        }

        for attempt in range(conf["max_retries"]):
            try:
                response = requests.post(conf["url"], headers=headers, json=payload, timeout=60)
                if response.status_code in [429, 503]:
                    time.sleep(10)
                    continue
                response.raise_for_status()
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                print(f"Ошибка API Анкеты (попытка {attempt + 1}): {e}")
                time.sleep(5)
        return None

    @staticmethod
    def get_gemini_response_for_theory(prompt):
        """Получает ответ от ИИ для теоретических вопросов"""
        settings = config.AI_THEORY_SETTINGS

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings['api_key']}"
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": settings['temperature'],
                "topP": settings['top_p']
            }
        }

        for attempt in range(settings['max_retries']):
            try:
                response = requests.post(settings['url'], headers=headers, json=payload, timeout=60)

                if response.status_code in [429, 503]:
                    time.sleep(10)
                    continue

                response.raise_for_status()
                data = response.json()

                return data["candidates"][0]["content"]["parts"][0]["text"]

            except Exception as e:
                print(f"Ошибка API (попытка {attempt + 1}): {e}")
                if attempt < settings['max_retries'] - 1:
                    time.sleep(5)

        return None

    @staticmethod
    def get_gemini_response_for_practice(prompt):
        """Получает ответ от ИИ для практических задач (код)"""
        settings = config.AI_PRACTICE_SETTINGS

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings['api_key']}"
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": settings['temperature'],
                "topP": settings['top_p']
            }
        }

        for attempt in range(settings['max_retries']):
            try:
                response = requests.post(settings['url'], headers=headers, json=payload, timeout=60)

                if response.status_code in [429, 503]:
                    time.sleep(10)
                    continue

                response.raise_for_status()
                data = response.json()

                return data["candidates"][0]["content"]["parts"][0]["text"]

            except Exception as e:
                print(f"Ошибка API (попытка {attempt + 1}): {e}")
                if attempt < settings['max_retries'] - 1:
                    time.sleep(5)

        return None