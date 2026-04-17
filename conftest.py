from playwright.sync_api import Page, expect
from time import sleep

import pytest
import os


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    auth_file = "auth_state.json"

    # Создаем базовый словарь настроек
    settings = {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},  # Устанавливаем размер окна
    }

    # Добавляем куки, если файл существует
    if os.path.exists(auth_file):
        settings["storage_state"] = auth_file

    return settings