class VacancyLocators:
    # Заголовок и описание
    TITLE_LOC = '[data-qa="vacancy-title"]'
    DESC_LOC = '[data-qa="vacancy-description"]'

    # Кнопки отклика и подтверждения
    RESPOND_BTN = '[data-qa="vacancy-response-link-top"]'
    CONFIRM_BTN_NAME = 'Всё равно откликнуться'
    RELOCATION_BTN = '[data-qa="relocation-warning-confirm"]'

    # Анкета (блоки и элементы внутри)
    TASK_BLOCKS = '[data-qa="task-body"]'
    TASK_QUESTION = '[data-qa="task-question"]'
    CELL_CONTENT = '[data-qa="cell-text-content"]'
    CELL_LABEL = 'label[data-qa="cell"]'
    ANY_TEXTAREA = 'textarea'

    # Поля ввода и отправки в модальном окне
    SUBMIT_POPUP_BTN = '[data-qa="vacancy-response-submit-popup"]'
    LETTER_TOGGLE = '[data-qa="vacancy-response-letter-toggle"]'
    # Используем CSS-селектор с перечислением через запятую (ИЛИ)
    LETTER_INPUT = 'textarea[name="letter"], [data-qa="vacancy-response-popup-form-letter-input"]'
    LETTER_SUBMIT_BTN = '[data-qa="vacancy-response-letter-submit"]'
    STANDARD_TEXTAREA_WRAPPER = '[data-qa="textarea-native-wrapper"] textarea'

    # Чат (чатик)
    CHATIK_ROOT = '[data-qa="chatik-root"]'
    CHATIK_LAYOUT = '#chatik-layout'
    RESPONSE_LINK_VIEW = '[data-qa="vacancy-response-link-view-topic"]'
    CHATIK_CHAT_MESSAGE_APPLICANT = '[data-qa="chatik-chat-message-applicant-action"]'
    CHATIK_NEW_MESSAGE_INPUT = '[data-qa="chatik-new-message-text"]'
    CHATIK_SEND_BTN = '[data-qa="chatik-do-send-message"]'