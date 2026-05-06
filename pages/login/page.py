import config

from pages.base.page import BasePage

from pages.login.locators import LoginLocators

class LoginPage(BasePage):

    def login(self):

        self.page.set_viewport_size({'width': config.WINDOW_WIDTH, 'height': config.WINDOW_HEIGHT})
        self.page.goto("https://hh.ru/login")

        # Скрипт замирает. Залогинься в открывшемся окне, пройди капчу и SMS.
        self.page.pause()

        # После того как залогинился, нажми 'Resume' в инспекторе.
