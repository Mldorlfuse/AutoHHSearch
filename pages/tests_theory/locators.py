class TheoryLocators:
    # Текст вопроса и блоки ответов
    QUESTION_CONTAINER = '[data-qa="text-description"]'
    # Селектор из твоего исходного кода для карточек ответов
    ANSWER_OPTIONS = 'label.magritte-card___kxw8G_4-1-24'
    ANSWER_OPTIONS_ALT = '[data-qa="test-answer-option"]'

    # Кнопки управления
    NEXT_BTN = '[data-qa="footer-next-button"]'
    FINISH_BTN = '[data-qa="footer-finish-button"]'
    MODAL_FINISH_BTN = '[data-qa="modal-finish-btn"]'

    # Состояния завершения
    RESULT_PAGE_TEXT = 'text="Посмотреть результаты"'
    RESULT_URL_PART = "applicant/contest_result"