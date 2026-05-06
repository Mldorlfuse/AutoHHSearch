import os

# --- ПУТИ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(BASE_DIR, "HH_Automation_Profile")

# --- Настройка ОС ---
OS = 'Win' # Win - Windows/Linux , Mac - Mac OS

# --- НАСТРОЙКИ БРАУЗЕРА ---
HEADLESS = False # False - Чтобы окно браузера появилось, True - Чтобы выполнение было в фоне
WINDOW_WIDTH = 1080 # Ширина окна
WINDOW_HEIGHT = 1920 # Высота окна
SLOW_MO = 500 # Задержка (можно не трогать)

# --- НАСТРОЙКИ ПОИСКА ---
SEARCH_MODE = 'total'  # 'new' или 'total'
SEARCH_PERIOD = "3"  # 1, 3, 7, 30, 0

# --- 1. НАСТРОЙКИ ДЛЯ ОТКЛИКОВ (СОПРООВОДИТЕЛЬНЫЕ) ---
AI_STANDARD_SETTINGS = {
    "api_key": "",
    "url": "",
    "temperature": 0.7,
    "top_p": 0.95,
    "max_retries": 10
}

# --- 2. НАСТРОЙКИ ДЛЯ АНКЕТ ВНУТРИ ОТКЛИКА ---
AI_FORM_SETTINGS = {
    "api_key": "",
    "url": "",
    "temperature": 0.3,
    "top_p": 0.9,
    "max_retries": 10
}

# --- 3. НАСТРОЙКИ ДЛЯ ТЕСТОВ (ТЕОРИЯ) ---
AI_THEORY_SETTINGS = {
    "api_key": "",
    "url": "",
    "temperature": 0.5,
    "top_p": 0.95,
    "max_retries": 10
}

# --- 4. НАСТРОЙКИ ДЛЯ ТЕСТОВ (ПРАКТИКА/КОД) ---
AI_PRACTICE_SETTINGS = {
    "api_key": "",
    "url": "",
    "temperature": 0.2, # Низкая температура важна для кода
    "top_p": 0.95,
    "max_retries": 10
}

# --- ПРОМПТЫ И КОНТЕКСТ ---
SYSTEM_PROMPT = """""" # Твой текст общего промпта для сопроводительного письма
RESUME_CONTEXT = """""" # Твой текст для резюме
FORM_INSTRUCTIONS = """Не пиши очень длинные ответы на вопросы, постарайся писать их более кратко и человечески
    ЗП: 80000 руб."""

# --- КОНСТАНТЫ ТЕСТОВ ---
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
    TRAINING = "Потренироваться"

class Level:
    BASIC = "Базовый"
    INTERMEDIATE = "Средний"
    ADVANCED = "Продвинутый"

TASKS_TO_RUN = [
    {
        "name": Skill.SQL,
        "mode": Mode.TRAINING,
        "level": Level.BASIC
    }
]
