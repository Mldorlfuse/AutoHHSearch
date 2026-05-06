import config

class SearchLocators:
    TAG = f'[data-qa="autosearch__results-counter_{config.SEARCH_MODE}"]'
    CARD_VACANCY = '[data-qa="vacancy-serp__vacancy"]'
    SEARCH_PERIOD_MENU = '[data-qa="search-period-menu"]'
    ORDER_BY = f'[data-qa="magritte-select-option-{config.SEARCH_PERIOD}"]'
    TITLE = '[data-qa="serp-item__title"]'
    VACANCY_RESPONSE = '[data-qa="vacancy-serp__vacancy_response"]'