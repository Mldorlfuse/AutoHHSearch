import time

import config

from pages.base.page import BasePage
from pages.vacancy.page import VacancyPage
from pages.search.locators import SearchLocators


class SearchPage(BasePage):
    def start_search(self):
        processed_vacancies = set()
        self.page.goto('https://hh.ru/applicant/autosearch.xml')

        while True:
            btn = self.page.locator(SearchLocators.TAG).first
            if not btn.is_visible(): break

            btn.click()
            if config.SEARCH_MODE == 'total':
                self.page.wait_for_selector(SearchLocators.CARD_VACANCY)
                self.page.locator(SearchLocators.SEARCH_PERIOD_MENU).click()
                self.page.locator(SearchLocators.ORDER_BY).click()
                time.sleep(3)

            self.page.wait_for_selector(SearchLocators.CARD_VACANCY)
            vacs = self.page.locator(SearchLocators.CARD_VACANCY).all()

            for div in vacs:
                title_loc = div.locator(SearchLocators.TITLE)
                if title_loc.count() == 0: continue

                v_id = title_loc.inner_text().strip()
                if v_id in processed_vacancies or div.locator(SearchLocators.VACANCY_RESPONSE).is_hidden():
                    continue

                print(f"Обработка: {v_id}")

                with self.page.context.expect_page() as new_page_info:
                    title_loc.click()

                new_tab = new_page_info.value
                new_tab.wait_for_load_state()

                # Работаем через VacancyPage
                vacancy_p = VacancyPage(new_tab)
                try:
                    vacancy_p.apply_to_vacancy()  # Вызов одной функции, которая делает всё
                except Exception as e:
                    print(f"Ошибка: {e}")

                new_tab.close()
                processed_vacancies.add(v_id)
                time.sleep(10)

            self.page.goto('https://hh.ru/applicant/autosearch.xml')