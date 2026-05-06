from playwright.sync_api import Page, expect, sync_playwright

import pytest
import config

from pages.app import App

@pytest.fixture()
def page():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            config.USER_DATA_DIR,
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO
        )
        page = context.new_page()
        page.set_viewport_size({'width': config.WINDOW_WIDTH, 'height': config.WINDOW_HEIGHT})
        yield page
        context.close()

@pytest.fixture
def app(page):
    return App(page)