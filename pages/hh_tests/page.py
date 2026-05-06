import re

from playwright.sync_api import Page

import config
from pages.base.page import BasePage
from pages.hh_tests.locators import HhTestsLocators
from pages.tests_theory.page import TestTheoryPage
from pages.tests_practice.page import TestPracticePage
from pages.test_card.page import TestCardPage

class HhTestsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.TestPracticePage = TestPracticePage(page)
        self.TestTheoryPage = TestTheoryPage(page)
        self.TestCardPage = TestCardPage(page)

    def start_tests(self):
        self.page.goto("https://hh.ru/applicant/skill_verifications/methods")
        print('\n')

        for task in config.TASKS_TO_RUN:
            skill_name = task["name"]
            print(f"🔎 Обработка навыка: {skill_name}")

            strict_skills = ["java", "javascript", "sql", "postgresql"]

            if skill_name.lower() in strict_skills:
                card = self.page.locator(HhTestsLocators.SKILLS_METHOD_CONTAINER).filter(
                    has=self.page.locator(HhTestsLocators.SKILL_TITLE,
                                     has_text=re.compile(rf"^{re.escape(skill_name)}$", re.I))
                )
            else:
                card = self.page.locator(HhTestsLocators.SKILLS_METHOD_CONTAINER).filter(has_text=skill_name)

            card = card.first

            if card.count() > 0:
                print(f"🎯 Кликаю по карточке: {skill_name}")

                card.scroll_into_view_if_needed()
                card.click()

                self.page.wait_for_timeout(2000)

                if self.TestCardPage.hh_test_setup(task):
                    print(f"✅ Тест {skill_name} успешно запущен!")

                    self.run_full_test(skill_name, task['mode'])
                else:
                    print(f"⚠️ Не удалось настроить или запустить тест для {skill_name}. Иду к следующему.")
            else:
                print(f"❓ Навык '{skill_name}' не найден в списке на странице.")

        print("\n🏁 Все задачи из конфига обработаны.")

    def run_full_test(self, skill_name, mode):
        """
        Универсальный цикл прохождения.
        Бот будет крутиться здесь, пока не встретит 'applicant/contest_result' или статус 'FINISH'.
        """
        print(f"🏁 Начало прохождения: {skill_name} | Режим: {mode}")

        while True:
            # Проверка URL перед каждым новым заданием
            if "applicant/contest_result" in self.page.url:
                print(f"🎉 Тест '{skill_name}' полностью пройден (достигнута страница результатов)!")
                self.page.goto("https://hh.ru/applicant/skill_verifications/methods")
                break

            if mode == config.Mode.THEORY:
                result = self.TestTheoryPage.solve_test_theory(skill_name)
            elif mode == config.Mode.PRACTICE:
                result = self.TestPracticePage.solve_test_practice(skill_name, mode)
            elif mode == config.Mode.TRAINING:
                result = self.TestPracticePage.solve_test_practice(skill_name, mode)
            else:
                print(f"❌ Неизвестный режим: {mode}")
                break

            if result == "FINISH":
                print(f"🎉 Тест '{skill_name}' полностью пройден!")
                self.page.goto("https://hh.ru/applicant/skill_verifications/methods")
                break
            elif result == "CONTINUE":
                # Небольшая пауза, чтобы страница успела обновиться после клика на 'Следующая задача'
                self.page.wait_for_timeout(3000)
                continue
            else:
                print(f"🛑 Процесс прерван из-за ошибки.")
                break
