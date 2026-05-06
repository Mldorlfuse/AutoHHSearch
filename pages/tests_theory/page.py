import json
import re
import random

from pages.base.page import BasePage
from pages.tests_theory.locators import TheoryLocators
from services.ai.ai_service import ServiceAi

class TestTheoryPage(BasePage):
    def solve_test_theory(self, skill_name):
        # Даем странице время прогрузиться
        self.page.wait_for_timeout(3000)

        print("🧠 Анализирую вопрос...")

        # 1. Проверка завершения теста — НО СНАЧАЛА ОТВЕЧАЕМ НА ВОПРОС!
        # Убираем преждевременную проверку finish_button

        # 2. Извлекаем HTML вопроса
        question_locator = self.page.locator(TheoryLocators.QUESTION_CONTAINER)
        if not question_locator.is_visible(timeout=5000):
            # Может быть страница результатов
            if self.page.get_by_text("Посмотреть результаты").is_visible():
                return "FINISH"
            print("❌ Вопрос не найден")
            return False

        # Используем inner_html() для контента вопроса
        question_content_html = question_locator.inner_html().strip()

        # 3. Извлекаем варианты ответов
        options_locators = self.page.locator(TheoryLocators.ANSWER_OPTIONS).all()

        # Если вариантов нет — проверяем, может тест завершён
        if not options_locators:
            if self.page.get_by_text("Посмотреть результаты").is_visible():
                return "FINISH"
            # Пробуем другие селекторы для вариантов
            options_locators = self.page.locator(TheoryLocators.ANSWER_OPTIONS_ALT).all()

        if not options_locators:
            print("❌ Варианты ответов не найдены")
            return False

        # Собираем HTML-содержимое каждого варианта
        options_html_list = [opt.inner_html().strip() for opt in options_locators]

        # 4. Запрос к ИИ с передачей HTML
        prompt = f"""
            Ты — ведущий эксперт (Senior) в области: {skill_name}.
            Твоя задача — выбрать правильный ответ, анализируя предоставленную HTML-разметку вопроса и вариантов.

            ВОПРОС (HTML):
            {question_content_html}

            ВАРИАНТЫ ОТВЕТОВ (HTML-массив):
            {json.dumps(options_html_list, ensure_ascii=False, indent=2)}

            ПРАВИЛА:
            1. Внимательно изучи код внутри тегов <code> или подобных.
            2. Верни СТРОГО текст выбранного варианта (как он виден пользователю).
            3. Если твой ответ не совпадает идеально — выбери наиболее подходящий.

            ВЕРНИ СТРОГО JSON (без маркдауна, без пояснений):
            {{
              "correct_option_text": "текст выбранного ответа"
            }}
            Верни только json, без комментариев и рассуждений
            """

        raw_response = ServiceAi.get_gemini_response_for_theory(prompt)

        # Защита от пустых ответов
        if not raw_response or not isinstance(raw_response, str):
            print(f"📡 API вернуло некорректный ответ. Жму наугад.")
            random.choice(options_locators).click()
            return self.click_next_button()

        ai_choice = None
        try:
            # Поиск JSON
            match = re.search(r'\{[^{}]*\}', raw_response, re.DOTALL)
            if match:
                json_str = match.group(0).strip()
                if "'" in json_str and '"' not in json_str:
                    json_str = json_str.replace("'", '"')
                try:
                    data = json.loads(json_str)
                    ai_choice = data.get("correct_option_text")
                except json.JSONDecodeError:
                    pass

            # Поиск по ключу напрямую
            if not ai_choice:
                key_match = re.search(r'"correct_option_text"\s*:\s*"([^"]*)"', raw_response)
                if key_match:
                    ai_choice = key_match.group(1)

            # Используем весь ответ как последний шанс
            if not ai_choice:
                ai_choice = raw_response.strip()
                if ai_choice.startswith('"') and ai_choice.endswith('"'):
                    ai_choice = ai_choice[1:-1]

        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")

        # Финальная проверка
        if not ai_choice:
            print("⚠️ Не удалось извлечь ответ. Жму наугад.")
            random.choice(options_locators).click()
            return self.click_next_button()

        # 5. Кликаем по варианту
        found = False
        ai_choice_lower = ai_choice.lower().strip()

        for opt_locator in options_locators:
            opt_text = opt_locator.inner_text().strip()
            opt_text_lower = opt_text.lower()

            if ai_choice_lower in opt_text_lower or opt_text_lower in ai_choice_lower:
                print(f"✅ ИИ выбрал: {opt_text}")
                opt_locator.click()
                found = True
                break

        if not found:
            print(f"⚠️ Сопоставление не удалось. Искали: '{ai_choice}'. Доступные варианты:")
            for i, opt in enumerate(options_locators):
                print(f"  {i + 1}. {opt.inner_text().strip()[:80]}")
            print("⚠️ Жму первый вариант")
            options_locators[0].click()

        # 6. Переход к следующему вопросу (или завершение)
        return self.click_next_button()

    def click_next_button(self):
        """
        Нажимает кнопку "Далее" или "Завершить".
        Возвращает "FINISH" если тест завершён, "CONTINUE" если идём дальше.
        """
        self.page.wait_for_timeout(500)

        # Проверяем кнопку "Далее"
        next_button = self.page.locator(TheoryLocators.NEXT_BTN)
        finish_button = self.page.locator(TheoryLocators.FINISH_BTN)

        if next_button.is_visible() and next_button.is_enabled():
            btn_text = next_button.inner_text().lower().strip()
            print(f"➡️ Нажимаю кнопку: '{btn_text}'")
            next_button.click()
            self.page.wait_for_timeout(1000)

            # После клика проверяем, не появилась ли страница результатов
            if "завершить" in btn_text or "finish" in btn_text:
                self.page.wait_for_timeout(2000)
                if TheoryLocators.RESULT_URL_PART in self.page.url or self.page.get_by_text("Посмотреть результаты").is_visible():
                    return "FINISH"

            return "CONTINUE"

        # Если кнопки нет — проверяем, может тест уже завершён
        if self.page.get_by_text(TheoryLocators.RESULT_PAGE_TEXT).is_visible():
            return "FINISH"

        finish_button = self.page.locator(TheoryLocators.FINISH_BTN)
        if finish_button.is_visible():
            finish_button.click()
            self.page.wait_for_timeout(2000)
            return "FINISH"

        # Может быть модальное окно с результатом
        modal_finish = self.page.locator(TheoryLocators.MODAL_FINISH_BTN)
        if modal_finish.is_visible():
            modal_finish.click()
            self.page.wait_for_timeout(2000)
            return "FINISH"

        print("⚠️ Кнопка перехода не найдена")
        return False