import os
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
        "name": Skill.CPP,
        "mode": Mode.THEORY,
        "level": Level.INTERMEDIATE
    },
    {
        "name": Skill.ALGORITHMS,
        "mode": Mode.PRACTICE,
        "level": Level.BASIC
    }
]


def test_test_setup(page, task):
    """
    Выполняет настройку и запуск теста внутри карточки навыка.
    """
    print(f"⚙️ Настройка теста: {task['name']} | {task['level']} | {task['mode']}")

    # 1. Выбор уровня сложности (Базовый / Средний / Продвинутый)
    # Ищем кнопку-таб по тексту уровня сложности
    level_tab = page.locator("button[role='tab']").filter(has_text=task['level'])

    if level_tab.is_visible():
        # Кликаем, только если таб еще не выбран (aria-selected="false")
        if level_tab.get_attribute("aria-selected") == "false":
            level_tab.click()
            page.wait_for_timeout(1000)  # Ждем подгрузки контента для этого уровня
    else:
        print(f"❌ Уровень {task['level']} не найден.")
        return False

    # 2. Выбор режима (Теория или Практика)
    # Используем data-qa из твоего HTML:
    # 'applicant-keyskills-verification-methods-kind-card-theory' или '-practice'
    mode_qa_part = "theory" if task['mode'] == Mode.THEORY else "practice"
    mode_selector = f"[data-qa='applicant-keyskills-verification-methods-kind-card-{mode_qa_part}']"

    mode_card = page.locator(mode_selector)

    if mode_card.is_visible():
        # Кликаем по карточке-выбору (label), чтобы активировать радио-кнопку
        # В твоем HTML input находится внутри label.magritte-card
        mode_card.locator("..").click()
        page.wait_for_timeout(500)
    else:
        print(f"❌ Режим {task['mode']} не найден.")
        return False

    # 3. Нажатие на кнопку "Начать тест"
    # В HTML кнопка имеет data-qa="applicant-keyskills-verification-methods-start-theory"
    # (она меняется в зависимости от выбора, но мы можем найти её по тексту)
    button_mode = f"[data-qa='applicant-keyskills-verification-methods-kind-card-{mode_qa_part}']"
    start_button = page.locator(button_mode)

    if start_button.is_visible() and start_button.is_enabled():
        print(f"🚀 Нажимаю 'Начать тест' для {task['name']}...")
        start_button.click()
        return True
    else:
        # Проверяем, может кнопка имеет другое имя (например, если тест уже в процессе)
        print(f"⚠️ Не удалось нажать кнопку старта. Возможно, тест уже начат или недоступен.")
        return False

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
        # Переход на страницу со списком всех тестов
        page.goto("https://hh.ru/applicant/skill_verifications/methods")
        print('\n')

        for task in TASKS_TO_RUN:
            skill_name = task["name"]
            print(f"🔎 Проверка навыка: {skill_name}")

            # 1. Ищем контейнер карточки, который содержит текст с названием навыка
            # В структуре HH это чаще всего div с определенным data-qa
            card = page.locator("[data-qa='skills-verification-method-container']").filter(has_text=skill_name)

            if card.count() > 0:
                # 2. Проверяем, не пройден ли уже этот навык (смотрим наличие плашки статуса)
                # Если на карточке уже есть лейбл уровня (Базовый/Средний), значит тест сдан
                status_label = card.locator(".card-bottom-wrapper--I92jcWfDbk0DlbYj").inner_text()

                if status_label:
                    print(f"✅ Навык '{skill_name}' уже имеет подтвержденный уровень. Пропускаю.")
                    continue

                print(f"🎯 Навык '{skill_name}' не подтвержден. Захожу в карточку...")

                # Скроллим к карточке и кликаем по ней
                card.scroll_into_view_if_needed()
                card.click()

                # --- МЕСТО ДЛЯ БУДУЩЕЙ ЛОГИКИ (Выбор уровня и режима) ---
                print(f"📍 Мы внутри карточки {skill_name}. Ожидаю 3 секунды и иду назад.")
                test_test_setup(page, task)

                # Возвращаемся на главную страницу для следующей итерации
                page.go_back()

                # Ждем появления карточек снова
                page.wait_for_selector("[data-qa='skills-verification-method-container']")
            else:
                print(f"❌ Карточка '{skill_name}' не найдена на странице.")

        print("\n🏁 Все задачи из конфига обработаны.")
        context.close()