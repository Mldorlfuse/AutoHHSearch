from pages.base.page import BasePage
from pages.login.page import LoginPage
from pages.resume.page import ResumePage
from pages.search.page import SearchPage
from pages.tests_practice.page import TestPracticePage
from pages.test_card.page import TestCardPage
from pages.hh_tests.page import HhTestsPage
from pages.tests_theory.page import TestTheoryPage
from pages.vacancy.page import VacancyPage

class App:
    def __init__(self, page):
        self.base_page = BasePage(page)
        self.login_page = LoginPage(page)
        self.resume_page = ResumePage(page)
        self.search_page = SearchPage(page)
        self.tests_practice = TestPracticePage(page)
        self.test_catd = TestCardPage(page)
        self.hh_tests = HhTestsPage(page)
        self.tests_theory = TestTheoryPage(page)
        self.vacancy = VacancyPage(page)