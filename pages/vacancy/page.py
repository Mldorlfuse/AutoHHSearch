import json
import time
import re
import config

from pages.base.page import BasePage
from services.ai.ai_service import ServiceAi
from pages.vacancy.locators import VacancyLocators

class VacancyPage(BasePage):
    def get_info(self):
        """Собирает текст вакансии для AI"""
        title = self.page.locator(VacancyLocators.TITLE_LOC).inner_text().strip()
        description = "\n".join([loc.inner_text().strip() for loc in self.page.locator(VacancyLocators.DESC_LOC).all()])
        return f"Название: {title}\nОписание: {description}"

    def apply_to_vacancy(self):
        """Главный метод: нажимает отклик и решает, что делать дальше"""
        self.page.set_viewport_size({'width': config.WINDOW_WIDTH, 'height': config.WINDOW_HEIGHT})

        if not self.page.locator(VacancyLocators.RESPOND_BTN).first.is_visible():
            return False

        info = self.get_info()
        self.page.locator(VacancyLocators.RESPOND_BTN).first.click()
        time.sleep(4)

        # Обработка промежуточных кнопок
        self._handle_confirm_modals()

        # Выбор режима: Анкета или Простое письмо
        if 'applicant/vacancy_response' in self.page.url:
            self.solve_form_with_ai(info)
        else:
            self._fill_standard_response(info)
        return True

    def _handle_confirm_modals(self):
        """Проверка кнопок 'Все равно откликнуться' и 'Релокация'"""
        confirm_btn = self.page.get_by_role("button", name=VacancyLocators.CONFIRM_BTN_NAME)
        relocation_btn = self.page.locator(VacancyLocators.RELOCATION_BTN)

        if confirm_btn.is_visible():
            confirm_btn.click()
        elif relocation_btn.is_visible():
            relocation_btn.click()
        time.sleep(3)

    def _fill_standard_response(self, info):
        """Заполнение обычного письма или чата"""
        cover_letter = ServiceAi.get_gemini_response(info)
        if not cover_letter: return

        # Если открылся чатик
        if self.page.locator(VacancyLocators.CHATIK_LAYOUT).is_visible():
            self.page.locator(VacancyLocators.RESPONSE_LINK_VIEW).nth(1).click()
            self.page.locator(VacancyLocators.CHATIK_CHAT_MESSAGE_APPLICANT).click()
            self.page.locator(VacancyLocators.CHATIK_NEW_MESSAGE_INPUT).first.press_sequentially(cover_letter)
            self.page.locator(VacancyLocators.CHATIK_SEND_BTN).click()
        # Если стандартное поле
        else:
            area = self.page.locator(VacancyLocators.STANDARD_TEXTAREA_WRAPPER).first
            area.press_sequentially(cover_letter)
            submit = self.page.locator(VacancyLocators.SUBMIT_POPUP_BTN)
            if not submit.is_visible():
                submit = self.page.locator(VacancyLocators.LETTER_SUBMIT_BTN)
            submit.click()
        print(f"Отклик на {self.page.locator(VacancyLocators.TITLE_LOC).inner_text().strip()} завершен. - {self.page.url}")
        print('---------')

    def solve_form_with_ai(self, vacancy_context):
        """Логика сложной анкеты"""
        task_blocks = self.page.locator(VacancyLocators.TASK_BLOCKS).all()
        form_structure = []

        for index, block in enumerate(task_blocks):
            q_el = block.locator(VacancyLocators.TASK_QUESTION)
            if q_el.count() == 0: continue

            item = {
                "id": index,
                "question": q_el.inner_text().strip(),
                "options": [opt.inner_text().strip() for opt in block.locator(VacancyLocators.CELL_CONTENT).all()]
            }
            if not item["options"] and block.locator(VacancyLocators.ANY_TEXTAREA).count() > 0:
                item["type"] = "textarea"
            form_structure.append(item)

        prompt = f"""
            ВАКАНСИЯ: {vacancy_context}
            Промпт для сопроводительного письма: {config.SYSTEM_PROMPT}
            Дополнительные инструкции: {config.FORM_INSTRUCTIONS}
            АНКЕТА: {json.dumps(form_structure, ensure_ascii=False)}

            ЗАДАЧА:
            1. Дай ответы на вопросы анкеты (answers). 
               ВАЖНО: Если вопрос типа "multi-choice", выбери все подходящие варианты и перечисли их через символ пайп "|". 
               Например: "SQL|Python/Bash"
            2. Напиши сопроводительное письмо (cover_letter).

            ВЕРНИ СТРОГО JSON:
            {{
              "answers": {{"ID_вопроса": "Текст или варианты через |"}},
              "cover_letter": "Текст письма"
            }}
            """

        raw_response = ServiceAi.get_gemini_response_for_questions(prompt)
        if not raw_response: return

        try:
            clean_json = re.sub(r'```json|```', '', raw_response).strip()
            data = json.loads(clean_json)
            ai_answers = data.get("answers", {})
            final_letter = data.get("cover_letter", "")

            for index, block in enumerate(task_blocks):
                answer_raw = ai_answers.get(str(index))
                if not answer_raw: continue

                selected_answers = [a.strip().lower() for a in str(answer_raw).split('|')]
                cells = block.locator(VacancyLocators.CELL_LABEL)
                textarea = block.locator(VacancyLocators.ANY_TEXTAREA)

                found_match = False
                custom_variant_cell = None

                if cells.count() > 0:
                    for i in range(cells.count()):
                        cell = cells.nth(i)
                        txt_node = cell.locator(VacancyLocators.CELL_CONTENT)
                        cell_text = txt_node.inner_text().strip().lower() if txt_node.count() > 0 else ""

                        if any(ans == cell_text for ans in selected_answers):
                            cell.click()
                            found_match = True

                        if any(word in cell_text for word in ["свой", "вариант", "другое"]):
                            custom_variant_cell = cell

                    if not found_match and custom_variant_cell:
                        custom_variant_cell.click()

                if textarea.count() > 0 and textarea.first.is_visible():
                    textarea.first.press_sequentially(str(answer_raw).replace("|", ", "))

            # Вставка письма
            letter_toggle = self.page.locator(VacancyLocators.LETTER_TOGGLE)
            if letter_toggle.is_visible(): letter_toggle.click()

            letter_input = self.page.locator(VacancyLocators.LETTER_INPUT).first
            letter_input.fill("")
            letter_input.press_sequentially(final_letter.replace('\\n', '\n'))

            self.page.locator(VacancyLocators.SUBMIT_POPUP_BTN).click()
            print(f"Анкета отправлена успешно - {self.page.url} ")
        except Exception as e:
            print(f"Ошибка заполнения анкеты: {e}")
        print('---------')
