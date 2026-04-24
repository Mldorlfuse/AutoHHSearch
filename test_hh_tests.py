import os
import requests
import json
import time
import re
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
        "level": Level.ADVANCED
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
    url = "https://api.proxyapi.ru/google/v1beta/models/gemini-2.5-flash-lite:generateContent"

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
    # Даем странице время прогрузиться (хотя лучше использовать ожидания Playwright)
    page.wait_for_timeout(3000)

    print("🧠 Анализирую вопрос...")

    # 1. Проверяем, не закончился ли тест (кнопка "Посмотреть результаты" или "Завершить")
    # Если видим кнопку завершения, пробуем нажать и выходим
    finish_button = page.locator('[data-qa="footer-finish-button"]')
    if finish_button.is_visible():
        print("🏁 Вижу кнопку завершения теста.")
        if finish_button.is_enabled():
            finish_button.click()
            return "FINISH"

    # 2. Извлекаем текст вопроса
    question_element = page.locator('[data-qa="text-description"]')
    if not question_element.is_visible(timeout=5000):
        # Если вопрос не появился за 5 сек, вероятно, тест окончен
        if page.get_by_text("Посмотреть результаты").is_visible():
            return "FINISH"
        print("❌ Вопрос не найден")
        return False

    question_text = question_element.inner_text().strip()

    # 3. Извлекаем варианты ответов
    options_locators = page.locator('label.magritte-card___kxw8G_4-1-24').all()
    options = [opt.inner_text().strip() for opt in options_locators]

    if not options:
        print("❌ Варианты ответов не найдены")
        return False

    # 4. Запрос к ИИ
    prompt = f"""
        Ты — ведущий эксперт (Senior) с 10-летним опытом в области: {skill_name}.
        Твоя задача — пройти сертификационный тест и выбрать ЕДИНСТВЕННЫЙ правильный ответ.

        ВОПРОС: {question_text}
        ВАРИАНТЫ:
        {json.dumps(options, ensure_ascii=False, indent=2)}

        ПРАВИЛА:
        1. Анализируй вопрос глубоко, учитывай терминологию.
        2. Выбери наиболее точный и профессиональный вариант.
        3. Если вопрос с подвохом, выбирай вариант, который соответствует лучшим практикам индустрии.

        ВЕРНИ СТРОГО JSON:
        {{
          "correct_option_text": "полная строка"
        }}
        """

    raw_response = get_gemini_response_for_questions(prompt)
    if not raw_response: return False

    try:
        clean_json = re.sub(r'```json|```', '', raw_response).strip()
        ai_choice = json.loads(clean_json).get("correct_option_text")
    except Exception as e:
        print(f"Ошибка парсинга ИИ: {e}")
        return False

    # 5. Кликаем по варианту
    found = False
    for opt_locator in options_locators:
        if ai_choice.lower() in opt_locator.inner_text().lower():
            print(f"✅ ИИ выбрал: {ai_choice}")
            opt_locator.click()
            found = True
            break

    if not found:
        print("⚠️ Сопоставление не удалось, жму первый вариант")
        options_locators[0].click()

    # 6. Кнопка "Дальше" или "Завершить"
    next_button = page.locator('[data-qa="footer-next-button"]')

    # Если кнопка "Дальше" есть и активна - жмем и продолжаем
    if next_button.is_visible() and next_button.is_enabled():
        # Проверяем текст кнопки. Если на ней написано "Завершить", это конец.
        btn_text = next_button.inner_text().lower()
        next_button.click()

        if "завершить" in btn_text:
            return "FINISH"
        return "CONTINUE"

    # Если кнопка финиша отдельная
    if finish_button.is_visible() and finish_button.is_enabled():
        finish_button.click()
        return "FINISH"

    return False

def solve_test_practice(page, skill_name):
    print(f"🛠 Работаю над практической задачей по {skill_name}...")

    max_attempts = 5
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

    elements = page.locator('.container--kRiqW2gfRA0N2vRi').all()
    task_text = ""
    if elements:
        for el in elements:
            text_part = el.inner_text().strip()
            if text_part:
                task_text += text_part + "\n"
    task_text = task_text.strip()

    while attempt <= max_attempts:
        print(f"🔄 Попытка {attempt} из {max_attempts}...")

        # 2. Формируем промпт
        if attempt == 1:
            prompt = f"Напиши код решения для задачи по {skill_name}.\nЗАДАЧА:\n{task_text}\nВЕРНИ ТОЛЬКО ЧИСТЫЙ КОД."
        else:
            prompt = f"Предыдущий код не прошел тесты. Исправь его.\nОШИБКИ ТЕСТОВ:\n{last_error}\nЗАДАЧА:\n{task_text}\nВЕРНИ ТОЛЬКО ИСПРАВЛЕННЫЙ ЧИСТЫЙ КОД."

        # 3. Получаем ответ от ИИ
        solution_code = get_gemini_response_for_practice(prompt)
        if solution_code is None:
            print(f"❌ ИИ не вернул ответ. Повторяю...")
            attempt += 1
            continue

        # Очистка кода от маркдауна и мыслей (thought)
        if "<|thought|>" in solution_code:
            solution_code = solution_code.split("</|thought|>")[-1]

        for lang in ["cpp", "python", "javascript", "php", "sql", "go", "java"]:
            solution_code = solution_code.replace(f"```{lang}", "")
        solution_code = solution_code.replace("```", "").strip()

        # 4. Вставка кода
        print("⌨️ Вставляю код в редактор...")
        try:
            page.evaluate("(code) => { "
                          "const editor = window.monaco.editor.getModels()[0]; "
                          "if (editor) editor.setValue(code); "
                          "}", solution_code)
        except Exception as e:
            print(f"⚠️ Ошибка Monaco API: {e}")
            page.click('.monaco-editor')
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.type(solution_code)

        page.wait_for_timeout(1000)

        # 5. Запуск тестов
        print("🧪 Запускаю тесты...")
        page.locator('[data-qa="execute-code-button"]').click()
        page.wait_for_timeout(6000)

        # 6. ПРОВЕРКА ПЕРВЫХ 3 ТЕСТ-КЕЙСОВ
        test_chips = page.locator('[data-qa="admin-test"]').all()
        all_tests_passed = True
        error_report = ""

        if not test_chips:
            # 1. Проверяем стандартный результат (как было)
            res_locator = page.locator('[data-qa="test-case-actual-result"]').first
            # 2. Проверяем специфическую ошибку синтаксиса SQL (из твоего HTML)
            sql_error_locator = page.locator('[data-qa="sql-run-error"]').first

            if sql_error_locator.is_visible():
                all_tests_passed = False
                # Извлекаем текст ошибки синтаксиса (например, ERROR: syntax error...)
                error_report = f"SQL ERROR: {sql_error_locator.inner_text().strip()}"
            elif res_locator.is_visible():
                res_text = res_locator.inner_text()
                if any(x in res_text.lower() for x in ["error", "exception", "trace", "expected", "не совпадает"]):
                    all_tests_passed = False
                    error_report = res_text
        else:
            # Проверяем первые 3 "чипса" (тест-кейса)
            chips_to_check = test_chips[:3]
            for index, chip in enumerate(chips_to_check):
                chip.click()
                page.wait_for_timeout(600)

                # Синхронное получение текста
                input_data = page.locator('[data-qa="test-case-input-data"]').inner_text().strip()
                expected = page.locator('[data-qa="test-case-expected-data"]').inner_text().strip()
                actual = page.locator('[data-qa="test-case-actual-result"]').inner_text().strip()

                # Проверка иконки ошибки внутри чипса
                has_error_icon = chip.locator('img[src*="error"]').count() > 0

                if expected != actual or has_error_icon:
                    all_tests_passed = False
                    error_report += f"\nОШИБКА В ТЕСТЕ {index + 1}:\nВходные: {input_data}\nОжидалось: {expected}\nПолучено: {actual}\n"
                    break  # Выходим из цикла при первой ошибке

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
            slow_mo=1000,
            args=["--start-maximized"]
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