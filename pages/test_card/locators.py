import config

class TestCardLocators:
    LEVEL_TAB = "button[role='tab']"
    PRACTICE_MODE = f"label:has(input[data-qa='applicant-keyskills-verification-methods-kind-card-practice'])"
    TRAINING_BTN_NAME = 'Потренироваться'
    START_TEST_BTN_NAME = 'Начать тест'
    NEXT_BTN = '[data-qa="modal-next-btn"]'
    START_TEST_BTN = '[data-qa="modal-start-btn"]'