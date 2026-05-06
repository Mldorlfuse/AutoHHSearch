
from pages.base.page import BasePage
from pages.resume.locators import ResumeLocators

class ResumePage(BasePage):

    def update_resume(self):
        self.page.goto('https://hh.ru/applicant/resumes')
        upd = self.page.locator(ResumeLocators.UPDATE_RESUME_BUTTON)
        if upd.is_visible():
            upd.click()
            print("Резюме обновлено.")