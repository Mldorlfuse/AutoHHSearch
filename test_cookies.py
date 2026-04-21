import os
from playwright.sync_api import sync_playwright

# Используем ОТДЕЛЬНУЮ папку для профиля автоматизации
user_data_dir = os.path.expanduser("~/Documents/HH_Automation_Profile")

def test_cookies():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            slow_mo=500
        )
        page = context.new_page()
        page.goto("https://hh.ru/login")

        print("У тебя есть время, чтобы залогиниться вручную...")
        # Скрипт замирает. Залогинься в открывшемся окне, пройди капчу и SMS.
        page.pause()

        # После того как залогинился, нажми 'Resume' в инспекторе.
        # Сохраняем куки в файл для pytest
        context.storage_state(path="auth_state.json")
        context.close()