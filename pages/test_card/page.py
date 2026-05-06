from pages.base.page import BasePage
from pages.test_card.locators import TestCardLocators

class TestCardPage(BasePage):
    def hh_test_setup(self, task):
        """Выполняет настройку и запуск теста внутри карточки навыка."""
        print(f"⚙️ Настройка теста: {task['name']} | {task['level']} | {task['mode']}")

        # 1. Выбор уровня сложности
        level_tab = self.page.locator(TestCardLocators.LEVEL_TAB).filter(has_text=task['level'])
        if level_tab.is_visible():
            if level_tab.get_attribute("aria-selected") == "false":
                level_tab.click()
                self.page.wait_for_timeout(1000)
        else:
            print(f"❌ Уровень {task['level']} не найден.")
            return False

        # 2. Выбор режима (Теория или Практика)
        if task['mode'] == "Теория":
            mode_qa_part = "theory"
        elif task['mode'] == "Практика":
            mode_qa_part = "practice"
        else:
            mode_qa_part = "trainingg"
        mode_card = self.page.locator(f"label:has(input[data-qa='applicant-keyskills-verification-methods-kind-card-{mode_qa_part}'])")

        if mode_card.is_visible():
            mode_card.click(force=True)
            self.page.wait_for_timeout(500)
        if mode_qa_part == "trainingg":
            self.page.locator(TestCardLocators.PRACTICE_MODE).click(
                force=True)
            self.page.wait_for_timeout(500)
        elif mode_qa_part != 'theory':
            print(f"❌ Режим {task['mode']} не найден.")
            return False

        # 3. Нажатие на кнопку "Начать тест"
        if mode_qa_part == "trainingg":
            start_button = self.page.locator(f"[data-qa='applicant-keyskills-verification-methods-start-{mode_qa_part}']")
            if not start_button.is_visible():
                start_button = self.page.get_by_role("button", name=TestCardLocators.TRAINING_BTN_NAME)

            if start_button.is_visible() and start_button.is_enabled():
                print(f"🚀 Нажимаю 'Потренироваться' для {task['name']}...")
                start_button.click()
                return True
            else:
                print(f"⚠️ Кнопка старта не активна или не найдена.")
                return False
        else:
            start_button = self.page.locator(f"[data-qa='applicant-keyskills-verification-methods-start-{mode_qa_part}']")
            if not start_button.is_visible():
                start_button = self.page.get_by_role("button", name=TestCardLocators.START_TEST_BTN_NAME)

            if start_button.is_visible() and start_button.is_enabled():
                print(f"🚀 Нажимаю 'Начать тест' для {task['name']}...")
                start_button.click()
                self.page.locator(TestCardLocators.NEXT_BTN).click()
                self.page.locator(TestCardLocators.START_TEST_BTN).click()
                return True
            else:
                print(f"⚠️ Кнопка старта не активна или не найдена.")
                return False