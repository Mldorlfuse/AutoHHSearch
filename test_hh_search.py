import os
import requests
import json
import time
import re
import pyperclip
from pynput.keyboard import Key, Controller
from playwright.sync_api import sync_playwright
import config  # Импортируем наш конфиг


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

def solve_form_with_ai(page, vacancy_context=""):
    task_blocks = page.locator('[data-qa="task-body"]').all()
    form_structure = []

    for index, block in enumerate(task_blocks):
        question_element = block.locator('[data-qa="task-question"]')
        if question_element.count() == 0: continue

        question = question_element.inner_text().strip()
        options = [opt.inner_text().strip() for opt in block.locator('[data-qa="cell-text-content"]').all()]
        is_checkbox = block.locator('input[type="checkbox"]').count() > 0
        textarea = block.locator('textarea')

        item = {"id": index, "question": question}
        if options:
            item["type"] = "multi-choice" if is_checkbox else "choice"
            item["options"] = options
        elif textarea.count() > 0 and textarea.first.is_visible():
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

    raw_response = get_gemini_response_for_questions(prompt)
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
            cells = block.locator('label[data-qa="cell"]')
            textarea = block.locator('textarea')

            found_match = False
            custom_variant_cell = None

            if cells.count() > 0:
                for i in range(cells.count()):
                    cell = cells.nth(i)
                    txt_node = cell.locator('[data-qa="cell-text-content"]')
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
        letter_toggle = page.locator('[data-qa="vacancy-response-letter-toggle"]')
        if letter_toggle.is_visible(): letter_toggle.click()

        letter_input = page.locator(
            'textarea[name="letter"], [data-qa="vacancy-response-popup-form-letter-input"]').first
        letter_input.fill("")
        letter_input.press_sequentially(final_letter.replace('\\n', '\n'))

        page.locator('[data-qa="vacancy-response-submit-popup"]').click()
        print(f"Анкета отправлена успешно - {page.url} ")
    except Exception as e:
        print(f"Ошибка заполнения анкеты: {e}")

def check_and_fill(vacancy_page):
    vacancy_page.set_viewport_size({'width': config.WINDOW_WIDTH, 'height': config.WINDOW_HEIGHT})
    try:
        respond_button = vacancy_page.locator('[data-qa="vacancy-response-link-top"]').first
        if not respond_button.is_visible(): return

        title = vacancy_page.locator('[data-qa="vacancy-title"]').inner_text()
        desc_locs = vacancy_page.locator('[data-qa="vacancy-description"]').all()
        description = "\n".join([loc.inner_text().strip() for loc in desc_locs if loc.inner_text().strip()])

        respond_button.click()
        time.sleep(5)

        # Подтверждения
        confirm_btn = vacancy_page.get_by_role("button", name="Всё равно откликнуться")
        relocation_btn = vacancy_page.locator('[data-qa="relocation-warning-confirm"]')

        if confirm_btn.is_visible():
            confirm_btn.click()
        elif relocation_btn.is_visible():
            relocation_btn.click()

        time.sleep(3)

        if 'applicant/vacancy_response' in vacancy_page.url:
            solve_form_with_ai(vacancy_page, f"Название: {title}\nОписание: {description}")
        else:
            cover_letter = get_gemini_response(f"Название: {title}\nОписание: {description}")
            if not cover_letter: return

            if vacancy_page.locator('[data-qa="chatik-root"]').is_hidden():
                area = vacancy_page.locator('[data-qa="textarea-native-wrapper"]').locator('textarea').first
                area.press_sequentially(cover_letter)
                submit = vacancy_page.locator('[data-qa="vacancy-response-submit-popup"]')
                if not submit.is_visible(): submit = vacancy_page.locator('[data-qa="vacancy-response-letter-submit"]')
                submit.click()
            elif vacancy_page.locator('#chatik-layout').is_visible():
                vacancy_page.locator('[data-qa="vacancy-response-link-view-topic"]').nth(1).click()
                vacancy_page.locator('[data-qa="chatik-chat-message-applicant-action"]').click()
                vacancy_page.locator('[data-qa="chatik-new-message-text"]').first.press_sequentially(cover_letter)
                vacancy_page.locator('[data-qa="chatik-do-send-message"]').click()
            print(f"Отклик на {title} завершен.")
    except Exception as e:
        print(f"Ошибка в check_and_fill: {e}")

def test_hh():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            config.USER_DATA_DIR,
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO
        )
        processed_vacancies = set()
        page = context.new_page()
        page.set_viewport_size({'width': config.WINDOW_WIDTH, 'height': config.WINDOW_HEIGHT})

        # Обновление резюме
        page.goto('https://hh.ru/applicant/resumes')
        upd = page.locator('[data-qa="resume-update-button resume-update-button_actions"]')
        if upd.is_visible():
            upd.click()
            print("Резюме обновлено.")

        page.goto('https://hh.ru/applicant/autosearch.xml')
        tag = f'[data-qa="autosearch__results-counter_{config.SEARCH_MODE}"]'

        while True:
            btn = page.locator(tag).first
            if not btn.is_visible(): break

            card = page.locator('[data-qa="autosearch-item"]').filter(has=btn).first
            title = card.locator('[data-qa="autosearch__title"]').inner_text().strip()
            print(f"\n>>> ПОИСК: {title}")
            btn.click()

            if config.SEARCH_MODE == 'total':
                page.wait_for_selector('[data-qa="vacancy-serp__vacancy"]')
                page.locator('[data-qa="search-period-menu"]').click()
                page.locator(f'[data-qa="order-by-{config.SEARCH_PERIOD}"]').click()
                time.sleep(3)

            page.wait_for_selector('[data-qa="vacancy-serp__vacancy"]')
            vacs = page.locator('[data-qa="vacancy-serp__vacancy"]').all()

            for div in vacs:
                try:
                    title_loc = div.locator('[data-qa="serp-item__title"]')
                    emp_loc = div.locator('[data-qa="vacancy-serp__vacancy-employer"]')
                    if title_loc.count() == 0: continue

                    v_name = title_loc.inner_text().strip()
                    e_name = emp_loc.inner_text().strip() if emp_loc.count() > 0 else "N/A"
                    v_id = f"{v_name}_{e_name}"

                    if v_id in processed_vacancies or div.locator(
                            '[data-qa="vacancy-serp__vacancy_response"]').is_hidden():
                        continue

                    print(f"Обработка: {v_name}")
                    with context.expect_page() as new_page_info:
                        title_loc.click()
                    v_page = new_page_info.value
                    v_page.wait_for_load_state()
                    check_and_fill(v_page)
                    v_page.close()
                    processed_vacancies.add(v_id)
                    time.sleep(12)
                except Exception as e:
                    print(f"Ошибка вакансии: {e}")

            page.goto('https://hh.ru/applicant/autosearch.xml')

        context.close()