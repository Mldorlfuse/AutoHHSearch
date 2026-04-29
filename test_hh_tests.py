import os
import requests
import json
import time
import re
import random
from pynput.keyboard import Key, Controller
from playwright.sync_api import sync_playwright

class Skill:
    API = "API"
    ENGLISH = "Английский"
    REGRESSION_TESTING = "Регрессионное тестирование"
    DOCKER = "Docker"
    GIT = "Git"
    FUNCTIONAL_TESTING = "Функциональное тестирование"
    HTML = "HTML"
    CSS = "CSS"
    JAVASCRIPT = "JavaScript"
    AGILE = "Agile Project Management"
    OOP = "ООП"
    SCRUM = "Scrum"
    PYTHON = "Python"
    AUTOCAD = "AutoCAD"
    CSHARP = "C#"
    CPP = "C++"
    GOLANG = "Golang"
    HR_ANALYTICS = "HR-аналитика"
    JAVA = "Java"
    MS_EXCEL = "MS Excel"
    OKR = "OKR"
    PHP = "PHP"
    ALGORITHMS = "Алгоритмы и структуры данных"
    COPYWRITING = "Копирайтинг"
    MATH_STATS = "Математическая статистика"
    MACHINE_LEARNING = "Машинное обучение"
    SQL = "SQL"
    LINUX = "Linux"
    POSTGRESQL = "PostgreSQL"

class Mode:
    THEORY = "Теория"
    PRACTICE = "Практика"

class Level:
    BASIC = "Базовый"
    INTERMEDIATE = "Средний"
    ADVANCED = "Продвинутый"

# Пример использования в конфиге:
TASKS_TO_RUN = [
    {
        "name": Skill.SQL,
        "mode": Mode.PRACTICE,
        "level": Level.INTERMEDIATE
    }
]


def get_gemini_response_for_questions(prompt):
    # Твой новый ключ от ProxyAPI (начинается на PA-...)
    api_key = "sk-Uzay8S0pApr49nG350VVRRRNbtsks7wu"

    # URL для ProxyAPI.
    # ВНИМАНИЕ: Убедись, что модель gemma-3-27b-it поддерживается прокси.
    # Если будет ошибка 404, используй: gemini-2.5-flash
    url = "https://api.proxyapi.ru/google/v1beta/models/gemini-2.5-flash-lite:generateContent"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # Ключ переехал сюда
    }

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95
        }
    }

    max_retries = 10
    for attempt in range(max_retries):
        try:
            # Убрали ?key= из URL
            response = requests.post(url, headers=headers, json=payload, timeout=60)

            # Стандартная обработка перегрузки
            if response.status_code in [429, 503]:
                time.sleep(10)
                continue

            response.raise_for_status()
            data = response.json()

            # Структура ответа остается такой же, как у оригинального Google API
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            print(f"Ошибка API (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)

    return None

def get_gemini_response_for_practice(prompt):
    # Твой ключ от ProxyAPI (замени на реальный)
    api_key = "sk-Uzay8S0pApr49nG350VVRRRNbtsks7wu"

    # Меняем URL на прокси-сервер
    # ВАЖНО: Убедись, что модель gemma-3-27b-it активна в ProxyAPI.
    # Если будет ошибка 404, попробуй gemini-2.5-flash
    url = "https://api.proxyapi.ru/google/v1beta/models/gemini-2.5-flash:generateContent"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95
        }
    }

    max_retries = 10
    for attempt in range(max_retries):
        try:
            # Выполняем запрос без ?key= в URL
            response = requests.post(url, headers=headers, json=payload, timeout=60)

            # Обработка лимитов и временных сбоев
            if response.status_code in [429, 503]:
                time.sleep(10)
                continue

            response.raise_for_status()
            data = response.json()

            # Структура ответа у ProxyAPI полностью совпадает с оригиналом Google
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            print(f"Ошибка API (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)

    return None

def hh_test_setup(page, task):
    """
    Выполняет настройку и запуск теста внутри карточки навыка.
    """
    print(f"⚙️ Настройка теста: {task['name']} | {task['level']} | {task['mode']}")

    # 1. Выбор уровня сложности
    level_tab = page.locator("button[role='tab']").filter(has_text=task['level'])
    if level_tab.is_visible():
        if level_tab.get_attribute("aria-selected") == "false":
            level_tab.click()
            page.wait_for_timeout(1000)
    else:
        print(f"❌ Уровень {task['level']} не найден.")
        return False

    # 2. Выбор режима (Теория или Практика)
    mode_qa_part = "theory" if task['mode'] == Mode.THEORY else "practice"
    # Ищем именно карточку, которая содержит этот input
    mode_card = page.locator(f"label:has(input[data-qa='applicant-keyskills-verification-methods-kind-card-{mode_qa_part}'])")

    if mode_card.is_visible():
        # Используем force=True, так как Magritte часто перекрывает элементы
        mode_card.click(force=True)
        page.wait_for_timeout(500)
    else:
        print(f"❌ Режим {task['mode']} не найден.")
        return False

    # 3. Нажатие на кнопку "Начать тест"
    # Используем точный data-qa для кнопки "Начать тест"
    start_button = page.locator(f"[data-qa='applicant-keyskills-verification-methods-start-{mode_qa_part}']")

    # Если кнопка не найдена по специфичному ID, ищем просто по тексту
    if not start_button.is_visible():
        start_button = page.get_by_role("button", name="Начать тест")

    if start_button.is_visible() and start_button.is_enabled():
        print(f"🚀 Нажимаю 'Начать тест' для {task['name']}...")
        start_button.click()
        page.locator('[data-qa="modal-next-btn"]').click()
        page.locator('[data-qa="modal-start-btn"]').click()
        return True
    else:
        print(f"⚠️ Кнопка старта не активна или не найдена.")
        return False

def solve_test_theory(page, skill_name):
    # Даем странице время прогрузиться
    page.wait_for_timeout(3000)

    print("🧠 Анализирую вопрос...")

    # 1. Проверка завершения теста
    finish_button = page.locator('[data-qa="footer-finish-button"]')
    if finish_button.is_visible():
        print("🏁 Вижу кнопку завершения теста.")
        if finish_button.is_enabled():
            finish_button.click()
            return "FINISH"

    # 2. Извлекаем HTML вопроса
    question_locator = page.locator('[data-qa="text-description"]')
    if not question_locator.is_visible(timeout=5000):
        if page.get_by_text("Посмотреть результаты").is_visible():
            return "FINISH"
        print("❌ Вопрос не найден")
        return False

    # Используем inner_html() для контента вопроса
    question_content_html = question_locator.inner_html().strip()

    # 3. Извлекаем варианты ответов (как объекты и как HTML для ИИ)
    options_locators = page.locator('label.magritte-card___kxw8G_4-1-24').all()

    # Собираем только HTML-содержимое каждого варианта
    options_html_list = [opt.inner_html().strip() for opt in options_locators]

    if not options_html_list:
        print("❌ Варианты ответов не найдены")
        return False

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

        ВЕРНИ СТРОГО JSON:
        {{
          "correct_option_text": "текст выбранного ответа"
        }}
        """

    raw_response = get_gemini_response_for_questions(prompt)

    # 1. Защита от пустых ответов при сбое API
    if not raw_response or not isinstance(raw_response, str):
        print(f"📡 API вернуло некорректный ответ (Error 500). Жму наугад.")
        options_locators[0].click()
        return "CONTINUE"

    ai_choice = None
    try:
        # 2. Улучшенный поиск JSON (ищет содержимое между { и })
        # Это спасет, если ИИ прислал "Вот ваш ответ: { ... }"
        match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            ai_choice = data.get("correct_option_text")
        else:
            # Если JSON вообще нет, пробуем считать весь текст как ответ (план Б)
            ai_choice = raw_response.strip()

    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")

    # 5. Кликаем по варианту (сопоставляем по чистому тексту)
    found = False
    for opt_locator in options_locators:
        # inner_text() уберет все теги и оставит чистую строку для сравнения
        if ai_choice.lower() in opt_locator.inner_text().lower():
            print(f"✅ ИИ выбрал: {opt_locator.inner_text().strip()}")
            opt_locator.click()
            found = True
            break

    if not found:
        print("⚠️ Сопоставление не удалось, жму первый вариант")
        options_locators[0].click()

    # 6. Переход к следующему вопросу
    page.wait_for_timeout(500)
    next_button = page.locator('[data-qa="footer-next-button"]')

    if next_button.is_visible() and next_button.is_enabled():
        btn_text = next_button.inner_text().lower()
        next_button.click()
        return "FINISH" if "завершить" in btn_text else "CONTINUE"

    return False

def solve_test_practice(page, skill_name):
    print(f"🛠 Работаю над практической задачей по {skill_name}...")

    time.sleep(5)

    max_attempts = 10
    attempt = 1
    last_error = ""

    # 1. Сбор описания задачи (ждем появления контейнера)
    try:
        page.wait_for_selector('.container--kRiqW2gfRA0N2vRi', timeout=15000)
    except:
        # Если контейнера нет, возможно мы уже на странице результатов
        if "applicant/contest_result" in page.url:
            return "FINISH"
        return "ERROR"

    while attempt <= max_attempts:
        print(f"🔄 Попытка {attempt} из {max_attempts}...")

        # ВАЖНО: Даем редактору время "прийти в себя" после прошлой печати
        page.wait_for_timeout(1000)

        elements = page.locator('.container--kRiqW2gfRA0N2vRi').all()

        description_text = ""
        current_code = ""
        error_report = ""

        if len(elements) >= 3:
            # 1. ОПИСАНИЕ ЗАДАЧИ
            description_text = elements[0].inner_text().strip()

            # 2. ТЕКУЩИЙ КОД (извлекаем по строкам из Monaco)
            elements[1].scroll_into_view_if_needed()
            line_locators = elements[1].locator('.view-line').all()

            # Если строк нет сразу, подождем отрисовки
            if not line_locators:
                page.wait_for_timeout(1000)
                line_locators = elements[1].locator('.view-line').all()

            code_lines = [line.inner_text().replace('\u00a0', ' ') for line in line_locators]
            current_code = "\n".join(code_lines)

            # 3. РЕЗУЛЬТАТЫ ТЕСТОВ И ОШИБКИ
            # Обычно это нижний блок, где написано "Ошибка в тесте 1..."
            error_report = elements[2].inner_text().strip()

        # Формируем итоговый task_text для промпта
        task_text = f"ОПИСАНИЕ ЗАДАЧИ:\n{description_text}\n\n"
        task_text += f"ТЕКУЩИЙ КОД В РЕДАКТОРЕ:\n{current_code}\n\n"
        task_text += f"ОШИБКИ И ТЕСТЫ:\n{error_report}"

        # 2. Формируем промпт

        if attempt == 1:
            prompt = f"Напиши код решения для задачи по {skill_name}.{task_text}ВЕРНИ ТОЛЬКО ЧИСТЫЙ КОД."
        else:
            prompt = f"Предыдущий код не прошел тесты. Исправь его. Не повторяй предыдущий код. {task_text}ВЕРНИ ТОЛЬКО ИСПРАВЛЕННЫЙ ЧИСТЫЙ КОД."

        # 3. Получаем ответ от ИИ
        solution_code = get_gemini_response_for_practice(prompt)
        if solution_code is None:
            print(f"❌ ИИ не вернул ответ. Повторяю...")
            attempt += 1
            continue

        # 3.1 Очистка кода от маркдауна и мыслей (thought)
        if "<|thought|>" in solution_code:
            solution_code = solution_code.split("</|thought|>")[-1]

        for lang in ["cpp", "python", "javascript", "php", "sql", "go", "java", "csharp"]:
            solution_code = solution_code.replace(f"```{lang}", "")
        solution_code = solution_code.replace("```", "").strip()

        def safe_clean_comments(text, lang_name):
            # Регулярка для строк в кавычках (чтобы их пропускать)
            # Находит "...", '...', """...""", '''...'''
            pattern = r'(\".*?\"|\'.*?\'|\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')'

            def replace_func(match):
                item = match.group(0)
                # Если это строка в кавычках — возвращаем как есть
                if item.startswith(('"', "'")):
                    return item
                return ""  # Если это был комментарий — удаляем

            # Выбираем правила в зависимости от языка (lang_name)
            if lang_name in ['python', 'sql']:
                # Для Python/SQL удаляем только однострочные # или --
                # Но только если они НЕ внутри кавычек
                comment_pattern = r'(\".*?\"|\'.*?\'|\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')|(#.*|--.*)'
            else:
                # Для C-style (Java, JS, C++, Go, PHP)
                # Удаляем //... и /*...*/
                comment_pattern = r'(\".*?\"|\'.*?\'|\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')|(/\*[\s\S]*?\*/|//.*)'

            return re.sub(comment_pattern, replace_func, text)

        # Определяем текущий язык из контекста задачи (skill_name)
        current_lang = skill_name.lower()

        # Очищаем, сохраняя структуру строк
        solution_code = safe_clean_comments(solution_code, current_lang)

        # 3.2. Удаляем лишние пустые строки, которые остались после комментариев
        lines = [line for line in solution_code.splitlines() if line.strip()]
        solution_code = "\n".join(lines).strip()

        print("✨ Код очищен (строки сохранены).")

        #todo Проверить что это работает

        # 4. Вставка кода (Посимвольная имитация печати)
        print("⌨️ Фокусируюсь на редакторе...")

        # Находим контейнер, который перехватывает клики (обычно это слой с текстом)
        editor_overlay = page.locator('.monaco-editor [data-qa="editor-content"]').first

        # Если такого нет, кликаем просто по самому блоку редактора
        if not editor_overlay.is_visible():
            editor_overlay = page.locator('.monaco-editor').first

        # Кликаем по визуальному слою, чтобы перевести фокус
        editor_overlay.click()

        # Теперь, когда фокус в редакторе, находим скрытую textarea
        # и используем force=True, чтобы Playwright не ругался на перекрытие
        editor_input = page.locator('.monaco-editor textarea').first
        editor_input.focus()

        page.wait_for_timeout(500)

        # Инициализируем контроллер клавиатуры
        keyboard = Controller()

        # 1. Фокусировка и подготовка
        page.bring_to_front()
        editor_overlay = page.locator('.monaco-editor').first
        editor_overlay.click()
        page.wait_for_timeout(500)

        # 2. Очистка (Cmd+A на Маке) через pynput
        print("🧹 Очищаю старый код...")
        with keyboard.pressed(Key.cmd):
            keyboard.press('a')
            keyboard.release('a')

        page.wait_for_timeout(200)
        keyboard.press(Key.backspace)
        keyboard.release(Key.backspace)
        page.wait_for_timeout(300)

        # 3. Подготовка текста
        lines = solution_code.split('\n')
        clean_solution_code = '\n'.join([line.lstrip() for line in lines])

        # Настройки для "умного" обхода
        brackets = {'(': ')', '[': ']', '{': '}'}
        quotes = {'"': '"', "'": "'"}
        skip_next_char = None

        print(f"🚀 Запуск системной печати через pynput ({len(clean_solution_code)} симв.)...")

        # Сбрасываем состояние модификаторов на всякий случай
        for k in [Key.cmd, Key.shift, Key.alt, Key.ctrl]:
            keyboard.release(k)

        for char in clean_solution_code:
            # --- ЛОГИКА ПЕРЕШАГИВАНИЯ ---
            if char == skip_next_char:
                keyboard.press(Key.right)
                keyboard.release(Key.right)
                skip_next_char = None
                continue

            # --- ПЕЧАТЬ СИМВОЛА ---
            if char == '\n':
                keyboard.press(Key.space)
                keyboard.release(Key.space)
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
                page.wait_for_timeout(random.randint(250, 450))
            elif char == '\t':
                keyboard.press(Key.space)
                keyboard.release(Key.space)
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
            elif char == ' ':
                keyboard.press(Key.space)
                keyboard.release(Key.space)
            else:
                # pynput.typewriter-style печать одного символа
                keyboard.type(char)

            # --- ЛОГИКА ПОСЛЕ ПЕЧАТИ (Автозаполнение Monaco) ---

            # Запоминаем кавычку, чтобы перешагнуть авто-пару
            if char in quotes:
                skip_next_char = quotes[char]
            else:
                skip_next_char = None

            # Удаляем авто-закрывающуюся скобку
            if char in brackets:
                page.wait_for_timeout(60)  # Даем Monaco время вставить пару
                keyboard.press(Key.right)
                keyboard.release(Key.right)
                keyboard.press(Key.backspace)
                keyboard.release(Key.backspace)

            # Пауза между символами (стабильность для macOS)
            page.wait_for_timeout(random.randint(25, 45))

        print("✅ Системная печать завершена.")

        # 5. Запуск тестов
        print("🧪 Запускаю тесты...")
        page.locator('[data-qa="execute-code-button"]').click()
        page.wait_for_timeout(6000)

        # 6. ПРОВЕРКА РЕЗУЛЬТАТОВ (SQL + ОБЩИЙ СЛУЧАЙ)
        test_chips = page.locator('[data-qa="admin-test"]').all()
        all_tests_passed = True
        error_report = ""

        # ПРОВЕРКА ДЛЯ SQL (табличный вид)
        sql_actual_locator = page.locator('[data-qa="sql-actual-result"]')
        sql_expected_locator = page.locator('[data-qa="sql-expected-result"]')
        sql_error_locator = page.locator('[data-qa="sql-run-error"]')

        if sql_error_locator.is_visible():
            # Случай 1: Ошибка в самом SQL запросе (синтаксис)
            all_tests_passed = False
            error_report = f"SQL SYNTAX ERROR: {sql_error_locator.inner_text().strip()}"

        elif sql_actual_locator.is_visible() and sql_expected_locator.is_visible():
            # Случай 2: Запрос выполнился, но нужно сравнить таблицы
            # Проверяем наличие плашки "Результат не сходится"
            mismatch_indicator = page.locator('[data-qa="chip"]:has-text("Результат не сходится")')

            if mismatch_indicator.is_visible():
                all_tests_passed = False
                actual_data = sql_actual_locator.inner_text().strip()
                expected_data = sql_expected_locator.inner_text().strip()
                error_report = (
                    f"SQL RESULT MISMATCH!\n"
                    f"--- ВАШ РЕЗУЛЬТАТ ---\n{actual_data}\n"
                    f"--- ОЖИДАЕМЫЙ РЕЗУЛЬТАТ ---\n{expected_data}\n"
                    f"Внимательно проверь порядок строк (ORDER BY) и точность значений."
                )

        # ПРОВЕРКА ДЛЯ ОБЫЧНЫХ ЗАДАЧ (Python/JS/PHP и т.д.)
        elif test_chips:
            chips_to_check = test_chips[:3]
            for index, chip in enumerate(chips_to_check):
                chip.click()
                page.wait_for_timeout(600)

                expected = page.locator('[data-qa="test-case-expected-data"]').inner_text().strip()
                actual = page.locator('[data-qa="test-case-actual-result"]').inner_text().strip()
                has_error_icon = chip.locator('img[src*="error"]').count() > 0

                if expected != actual or has_error_icon:
                    all_tests_passed = False
                    error_report += f"\nОШИБКА В ТЕСТЕ {index + 1}:\nОжидалось: {expected}\nПолучено: {actual}\n"
                    break

        elif page.locator('[data-qa="test-case-actual-result"]').first.is_visible():
            # Стандартная проверка одиночного результата
            res_locator = page.locator('[data-qa="test-case-actual-result"]').first
            res_text = res_locator.inner_text()
            if any(x in res_text.lower() for x in ["error", "exception", "expected", "не совпадает"]):
                all_tests_passed = False
                error_report = res_text

        if all_tests_passed:
            print("✅ Все тесты пройдены!")
            submit_btn = page.locator('[data-qa="submit-solution-button"]')
            if submit_btn.is_enabled():
                print("➡️ Нажимаю 'Отправить решение'...")
                submit_btn.click()
                page.wait_for_timeout(4000)

                if "assessment.hh.ru/code" in page.url:
                    return "CONTINUE"

                # Если кнопки "Следующая" нет, проверяем не попали ли мы на финиш
                if "applicant/contest_result" in page.url:
                    return "FINISH"

                # Запасной вариант: если нет кнопки, но и не финиш, подождем и проверим еще раз
                page.wait_for_timeout(2000)
                if "applicant/contest_result" in page.url:
                    return "FINISH"

                return "FINISH"
        else:
            last_error = error_report
            attempt += 1
            continue

    print("⚠️ Попытки исчерпаны.")
    return "ERROR"

def run_full_test(page, skill_name, mode):
    """
    Универсальный цикл прохождения.
    Бот будет крутиться здесь, пока не встретит 'applicant/contest_result' или статус 'FINISH'.
    """
    print(f"🏁 Начало прохождения: {skill_name} | Режим: {mode}")

    while True:
        # Проверка URL перед каждым новым заданием
        if "applicant/contest_result" in page.url:
            print(f"🎉 Тест '{skill_name}' полностью пройден (достигнута страница результатов)!")
            page.goto("https://hh.ru/applicant/skill_verifications/methods")
            break

        if mode == Mode.THEORY:
            result = solve_test_theory(page, skill_name)
        elif mode == Mode.PRACTICE:
            result = solve_test_practice(page, skill_name)
        else:
            print(f"❌ Неизвестный режим: {mode}")
            break

        if result == "FINISH":
            print(f"🎉 Тест '{skill_name}' полностью пройден!")
            page.goto("https://hh.ru/applicant/skill_verifications/methods")
            break
        elif result == "CONTINUE":
            # Небольшая пауза, чтобы страница успела обновиться после клика на 'Следующая задача'
            page.wait_for_timeout(3000)
            continue
        else:
            print(f"🛑 Процесс прерван из-за ошибки.")
            break

def test_hh_navigation():
    user_data_dir = os.path.expanduser("~/Documents/HH_Automation_Profile")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            slow_mo=10,
            args=["--start-maximized"],
            permissions = ['clipboard-write']
        )

        page = context.new_page()
        page.set_viewport_size({'width': 1080, 'height': 1820})
        # Переход на страницу со списком всех тестов
        page.goto("https://hh.ru/applicant/skill_verifications/methods")
        print('\n')

        for task in TASKS_TO_RUN:
            skill_name = task["name"]
            print(f"🔎 Обработка навыка: {skill_name}")

            strict_skills = ["java", "javascript", "sql", "postgresql"]

            if skill_name.lower() in strict_skills:
                # Вместо поиска по всей карточке, ищем строгое совпадение в заголовке внутри карточки
                # Это гарантирует, что SQL не найдет PostgreSQL
                card = page.locator("[data-qa='skills-verification-method-container']").filter(
                    has=page.locator("[data-qa='verification-method-title']",
                                     has_text=re.compile(rf"^{re.escape(skill_name)}$", re.I))
                )
            else:
                # Для остальных навыков оставляем как было (поиск подстроки во всей карточке)
                card = page.locator("[data-qa='skills-verification-method-container']").filter(has_text=skill_name)

            # Обязательный .first для предотвращения ошибки strict mode violation
            card = card.first

            if card.count() > 0:
                print(f"🎯 Кликаю по карточке: {skill_name}")

                # Скроллим и заходим внутрь
                card.scroll_into_view_if_needed()
                card.click()

                # Пауза для прогрузки интерфейса настройки
                page.wait_for_timeout(2000)

                # 1. Настраиваем уровень и режим (Теория/Практика), нажимаем "Начать тест"
                if hh_test_setup(page, task):
                    print(f"✅ Тест {skill_name} успешно запущен!")

                    # 2. Запускаем основной цикл прохождения
                    # Передаем mode из конфига, чтобы скрипт знал, какой алгоритм решения использовать
                    run_full_test(page, skill_name, task['mode'])
                else:
                    print(f"⚠️ Не удалось настроить или запустить тест для {skill_name}. Иду к следующему.")
            else:
                print(f"❓ Навык '{skill_name}' не найден в списке на странице.")

        print("\n🏁 Все задачи из конфига обработаны.")
        context.close()