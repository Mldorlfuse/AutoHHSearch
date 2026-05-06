class TestPracticeLocators:
    # Контейнеры и описание
    # Контейнеры с текстом задачи, кодом и ошибками
    MAIN_CONTAINER = '.container--kRiqW2gfRA0N2vRi'
    # Строки кода в редакторе Monaco
    CODE_LINES = '.view-line'

    # Редактор и управление
    # Кнопка "Запустить тесты"
    EXECUTE_BTN = '[data-qa="execute-code-button"]'
    # Кнопка "Отправить решение"
    SUBMIT_SOLUTION_BTN = '[data-qa="submit-solution-button"]'
    # Кнопка "Завершить тренировку" (для режима Training)
    FINISH_TRAINING_BTN = '[data-qa="finish-training-button"]'
    # Сам оверлей редактора (для кликов и фокуса)
    MONACO_EDITOR = '.monaco-editor'

    # Проверка результатов (Тест-кейсы)
    # Плашки (чипсы) отдельных тестов
    TEST_CHIPS = '[data-qa="admin-test"]'
    # Ожидаемый результат в деталях теста
    EXPECTED_DATA = '[data-qa="test-case-expected-data"]'
    # Фактический результат в деталях теста
    ACTUAL_DATA = '[data-qa="test-case-actual-result"]'
    # Иконка ошибки в чипсе
    ERROR_ICON_CSS = 'img[src*="error"]'

    # Специфичные локаторы для SQL
    SQL_ACTUAL = '[data-qa="sql-actual-result"]'
    SQL_EXPECTED = '[data-qa="sql-expected-result"]'
    SQL_ERROR = '[data-qa="sql-run-error"]'
    # Индикатор несовпадения результатов
    MISMATCH_CHIP = '[data-qa="chip"]:has-text("Результат не сходится")'