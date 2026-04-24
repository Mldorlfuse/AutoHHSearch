import os
import requests
import json
import time
import pytest
import re
from playwright.sync_api import sync_playwright

user_data_dir = os.path.expanduser("~/Documents/HH_Automation_Profile")

# Промпт оставляем без изменений (я его сократил в примере для краткости)
system_prompt = """Ты — опытный карьерный консультант и копирайтер. Твоя задача — написать идеальное сопроводительное письмо отклика на вакансию.

ПРАВИЛА И ОГРАНИЧЕНИЯ:
1. ЖЕСТКИЙ ЛИМИТ ОБЪЕМА: Твой ответ должен быть максимально кратким. Ответь кратко, Лимит 400 токенов
2. СТРУКТУРА:
   - Приветствие и название должности.
   - 1-2 главных аргумента из резюме, почему кандидат идеально подходит (только факты, без клише вроде "я коммуникабельный").
   - Вежливый призыв к действию (готовность к интервью).
3. ТОН: Профессиональный, уверенный, лаконичный. Без лишних расшаркиваний и лести.

Напиши ТОЛЬКО текст сопроводительного письма, без вступительных фраз вроде "Вот ваше письмо:".

Начинай сопроводительное письмо с простого приветствия, к примеру "Добрый день!"

Меня зовут - Марков Александр

Вконце письма всегда пиши : "
С уважением,
Марков Александр
Telegram: https://t.me/Mldorlfuse
+7 912 461-14-11
sania.4game@gmail.com

Мое резюме - Тестировщик
Уровень дохода не указан
Тип занятости: Стажировка, Постоянная работа, Подработка
Формат работы: На месте работодателя, Гибрид, Удалённо
Желательное время в пути до работы: Не имеет значения
Командировки: Могу
Редактировать
Контакты
Мобильный телефон
+7 912 461-14-11
Электронная почта — предпочитаемый способ связи
sania.4game@gmail.com

Опыт работы: 4 года 8 месяцев
Добавить
ООО Локал Интернет
2 года и 4 месяца
Тестировщик
Январь 2024 — сейчас (2 года и 4 месяца)

Проект:
Продуктовая IT-компания и стартап-инкубатор в сфере интернет-маркетинга. Входит в число лидеров по объему аудитории в своем сегменте (5 млн+ MAU). Специализируется на разработке внутренних highload-проектов и работе с CPA-рынком.

Стек:
Postman, DevTools, DBeaver, Git, MySQL, Figma, Kibana, Kafka, Jira, Playwright, Python

Обязанности:
- Проводил тестирование веб-приложения: UI, адаптивность, кроссбраузерность, анализ сетевых запросов через DevTools и Charles.
- Проверял backend: REST API, корректность обработки запросов, валидацию данных,
бизнес-логику и интеграции.
- Работал с MySQL через DBeaver: выполнял SQL-запросы для проверки данных, подготовки
тестовых сценариев и анализа дефектов.
- Анализировал логи сервисов в Kibana, отслеживал ошибки и цепочку вызовов между
микросервисами.
- Разрабатывал API и UI автотесты на стеке: Playwright, Python
- Проверял работу брокеров сообщений (Kafka): валидировал события, структуру сообщений и порядок обработки.
- Создавал и поддерживал тестовую документацию: чек-листы, тест-кейсы, API-спеки.
- Заводил баг-репорты, контролировал исправления, участвовал в обсуждении дефектов с
командами разработки.
- Участвовал в grooming-сессиях и уточнении требований, предлагал улучшения логики и UX

Достижения:
- Предотвратил попадание в продакшн 200+ критических багов, систематизировав выявление дефектов и обеспечив их оперативное исправление на ранних этапах.
- За счёт автоматизации e2e и регрес-тестов сократил объём ручных проверок примерно на
40–50%, переведя ключевые проверки работы с данными и нагрузкой в автотесты.
- Перестроил тестовую базу (600+ кейсов): сократил объём за счёт исключения неактуальных
сценариев, внедрил приоритеты, тем самым ускорил регресс и повысил качество покрытия.
Свернуть
amoCRM
amoCRM
2 года и 4 месяца
Тестировщик / Руководитель группы техческой поддержки 2-й линии
Сентябрь 2021 — Декабрь 2023 (2 года и 4 месяца)
Проект:
Проект:
amoCRM — ведущая SaaS-платформа для управления продажами и автоматизации бизнес-процессов. Высоконагруженная система с миллионами активных пользователей, включающая в себя сложную экосистему интеграций (мессенджеры, телефония, почта), микросервисную архитектуру и инструменты для кастомизации через API и виджеты.

Стек:
Jira, Kibana, Postman, DevTools, SQL, Wiki/Confluence.

Обязанности:
- Управление и процессы: Организовал процессы ночного тестирования и выстроил систему обработки инцидентов 24/7 для обеспечения бесперебойной работы.
- Взаимодействие: Настроил workflow взаимодействия между отделом тестирования, техподдержкой и разработкой, что ускорило передачу информации о багах и сократило Time-to-Fix.
- Техническая поддержка (L2/L3): Анализировал обращения пользователей, воспроизводил сложные дефекты и транслировал их в понятные технические требования для разработки.
- QA-инжиниринг: Проводил функциональное и регрессионное тестирование веб-приложений, анализировал сетевые запросы и логи систем в Kibana.
- Работа с данными: Контролировал своевременность передачи данных и корректность обработки инцидентов в рамках SLA.
- Документация: Создавал и поддерживал актуальность тестовой документации (чек-листы, тест-кейсы) и регламентов по обработке дефектов.
- Менторство: Обучил 12 сотрудников техникам поиска багов, работе в Jira и стандартам написания отчётов.

Достижения:
- Оптимизация реакции: За счет внедрения процессов инцидент-менеджмента и ночного тестирования значительно сократил время реакции на критические ошибки в продакшене.
- Повышение качества: Сформировал сильную команду из 12 специалистов «с нуля», внедрив единые стандарты качества и техники тест-дизайна, что снизило количество пропущенных дефектов.
- Прозрачность процессов: Полностью перестроил бизнес-процессы взаимодействия команд, обеспечив прозрачный трекинг каждой ошибки от момента обращения в поддержку до деплоя фикса.
Навыки
Продвинутый уровень
Git
REST API
User Interface
Функциональное тестирование
Регрессионное тестирование
Тестирование пользовательского интерфейса
JSON
Модульное тестирование
XML
SOAP
Test case
Сквозное тестирование
Средний уровень
SQL
PostgreSQL
Docker
Кроссбраузерное тестирование
Интеграционное тестирование
Ручное тестирование
API
Kibana
Apache Kafka
Проведение тестирований
CI/CD
Agile
Системное тестирование
Базовый уровень
Linux
Образование
Добавить
Удгу
Информационная безопасность
2019 · Высшее

Подтверждение навыков
Подтверждайте навыки — это выделит вас среди других кандидатов
API
Регрессионное тестирование
Docker
Git
Функциональное тестирование
Linux
...
Курсы по профессии «Тестировщик»
Посмотрите на карьерной платформе от hh.ru

О себе
QA Engineer с 5 годами опыта в тестировании веб-приложений, REST API и мобильных
продуктов. Регулярно работаю с Postman для проверки API, контрактов и
соответствия спецификаций. Использую базы данных и логи для анализа бизнес-логики,
поиска корневых причин дефектов и валидации данных.
Хорошо понимаю процессы SDLC/STLC, участвую в разборе требований, спринт-
планировании и командных ревью. Внимателен к деталям, ответственен за результат,
быстро онборжусь в новые проекты и фокусируюсь на повышении качества и
стабильности продукта.

Контакты:
- Telegram: @Mldorlfuse

Примеры автотестов:
- API: https://github.com/Mldorlfuse/AutoTestsPetstoreAPI (pytest)
- UI: https://github.com/Mldorlfuse/AutomationExerciveUI (pytest, selenium)
- UI: https://github.com/Mldorlfuse/AutoTestSwagLabsUI (pytest, playwright)

Наша цель - чтобы меня взяли. Поэтому можешь смело приукрашивать или откровенно врать


Ответ пиши только сопроводитлеьное письмо, чтобы я мог его скопировать. Лишнего текста не нужно. И без форматирования жирным, используй только абзацы и "-" для пунктов


Всталяй ссылку без гипер ссылок, просто как текст

Обязательно пиши на русском языке

Ниже будет текст вакансии
"""

resume_context = """
Тестировщик
Уровень дохода не указан
Тип занятости: Стажировка, Постоянная работа, Подработка
Формат работы: На месте работодателя, Гибрид, Удалённо
Желательное время в пути до работы: Не имеет значения
Командировки: Могу
Редактировать
Контакты
Мобильный телефон
+7 912 461-14-11
Электронная почта — предпочитаемый способ связи
sania.4game@gmail.com

Опыт работы: 4 года 8 месяцев
Добавить
ООО Локал Интернет
2 года и 4 месяца
Тестировщик
Январь 2024 — сейчас (2 года и 4 месяца)

Проект:
Продуктовая IT-компания и стартап-инкубатор в сфере интернет-маркетинга. Входит в число лидеров по объему аудитории в своем сегменте (5 млн+ MAU). Специализируется на разработке внутренних highload-проектов и работе с CPA-рынком.

Стек:
Postman, DevTools, DBeaver, Git, MySQL, Figma, Kibana, Kafka, Jira, Playwright, Python

Обязанности:
- Проводил тестирование веб-приложения: UI, адаптивность, кроссбраузерность, анализ сетевых запросов через DevTools и Charles.
- Проверял backend: REST API, корректность обработки запросов, валидацию данных,
бизнес-логику и интеграции.
- Работал с MySQL через DBeaver: выполнял SQL-запросы для проверки данных, подготовки
тестовых сценариев и анализа дефектов.
- Анализировал логи сервисов в Kibana, отслеживал ошибки и цепочку вызовов между
микросервисами.
- Разрабатывал API и UI автотесты на стеке: Playwright, Python
- Проверял работу брокеров сообщений (Kafka): валидировал события, структуру сообщений и порядок обработки.
- Создавал и поддерживал тестовую документацию: чек-листы, тест-кейсы, API-спеки.
- Заводил баг-репорты, контролировал исправления, участвовал в обсуждении дефектов с
командами разработки.
- Участвовал в grooming-сессиях и уточнении требований, предлагал улучшения логики и UX

Достижения:
- Предотвратил попадание в продакшн 200+ критических багов, систематизировав выявление дефектов и обеспечив их оперативное исправление на ранних этапах.
- За счёт автоматизации e2e и регрес-тестов сократил объём ручных проверок примерно на
40–50%, переведя ключевые проверки работы с данными и нагрузкой в автотесты.
- Перестроил тестовую базу (600+ кейсов): сократил объём за счёт исключения неактуальных
сценариев, внедрил приоритеты, тем самым ускорил регресс и повысил качество покрытия.
Свернуть
amoCRM
amoCRM
2 года и 4 месяца
Тестировщик / Руководитель группы техческой поддержки 2-й линии
Сентябрь 2021 — Декабрь 2023 (2 года и 4 месяца)
Проект:
Проект:
amoCRM — ведущая SaaS-платформа для управления продажами и автоматизации бизнес-процессов. Высоконагруженная система с миллионами активных пользователей, включающая в себя сложную экосистему интеграций (мессенджеры, телефония, почта), микросервисную архитектуру и инструменты для кастомизации через API и виджеты.

Стек:
Jira, Kibana, Postman, DevTools, SQL, Wiki/Confluence.

Обязанности:
- Управление и процессы: Организовал процессы ночного тестирования и выстроил систему обработки инцидентов 24/7 для обеспечения бесперебойной работы.
- Взаимодействие: Настроил workflow взаимодействия между отделом тестирования, техподдержкой и разработкой, что ускорило передачу информации о багах и сократило Time-to-Fix.
- Техническая поддержка (L2/L3): Анализировал обращения пользователей, воспроизводил сложные дефекты и транслировал их в понятные технические требования для разработки.
- QA-инжиниринг: Проводил функциональное и регрессионное тестирование веб-приложений, анализировал сетевые запросы и логи систем в Kibana.
- Работа с данными: Контролировал своевременность передачи данных и корректность обработки инцидентов в рамках SLA.
- Документация: Создавал и поддерживал актуальность тестовой документации (чек-листы, тест-кейсы) и регламентов по обработке дефектов.
- Менторство: Обучил 12 сотрудников техникам поиска багов, работе в Jira и стандартам написания отчётов.

Достижения:
- Оптимизация реакции: За счет внедрения процессов инцидент-менеджмента и ночного тестирования значительно сократил время реакции на критические ошибки в продакшене.
- Повышение качества: Сформировал сильную команду из 12 специалистов «с нуля», внедрив единые стандарты качества и техники тест-дизайна, что снизило количество пропущенных дефектов.
- Прозрачность процессов: Полностью перестроил бизнес-процессы взаимодействия команд, обеспечив прозрачный трекинг каждой ошибки от момента обращения в поддержку до деплоя фикса.
Навыки
Продвинутый уровень
Git
REST API
User Interface
Функциональное тестирование
Регрессионное тестирование
Тестирование пользовательского интерфейса
JSON
Модульное тестирование
XML
SOAP
Test case
Сквозное тестирование
Средний уровень
SQL
PostgreSQL
Docker
Кроссбраузерное тестирование
Интеграционное тестирование
Ручное тестирование
API
Kibana
Apache Kafka
Проведение тестирований
CI/CD
Agile
Системное тестирование
Базовый уровень
Linux
Образование
Добавить
Удгу
Информационная безопасность
2019 · Высшее

Подтверждение навыков
Подтверждайте навыки — это выделит вас среди других кандидатов
API
Регрессионное тестирование
Docker
Git
Функциональное тестирование
Linux
...
Курсы по профессии «Тестировщик»
Посмотрите на карьерной платформе от hh.ru

О себе
QA Engineer с 5 годами опыта в тестировании веб-приложений, REST API и мобильных
продуктов. Регулярно работаю с Postman для проверки API, контрактов и
соответствия спецификаций. Использую базы данных и логи для анализа бизнес-логики,
поиска корневых причин дефектов и валидации данных.
Хорошо понимаю процессы SDLC/STLC, участвую в разборе требований, спринт-
планировании и командных ревью. Внимателен к деталям, ответственен за результат,
быстро онборжусь в новые проекты и фокусируюсь на повышении качества и
стабильности продукта.

Контакты:
- Telegram: @Mldorlfuse

Примеры автотестов:
- API: https://github.com/Mldorlfuse/AutoTestsPetstoreAPI (pytest)
- UI: https://github.com/Mldorlfuse/AutomationExerciveUI (pytest, selenium)
- UI: https://github.com/Mldorlfuse/AutoTestSwagLabsUI (pytest, playwright)
"""


def get_gemini_response(vacancy_text):
    # Замени на свой реальный ключ от ProxyAPI
    api_key = "sk-Uzay8S0pApr49nG350VVRRRNbtsks7wu"

    # URL меняем на прокси-адрес (используем flash-lite, как в твоем примере)
    url = "https://api.proxyapi.ru/google/v1beta/models/gemini-2.5-flash-lite:generateContent"

    # Теперь Authorization Bearer обязателен
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    full_prompt = f"{system_prompt}\n\nВАКАНСИЯ:\n{vacancy_text}"

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95
        }
    }

    max_retries = 10
    for attempt in range(max_retries):
        try:
            # Важно: убираем ?key= из URL, так как ключ теперь в заголовках
            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code in [429, 503]:
                time.sleep(10)
                continue

            response.raise_for_status()
            data = response.json()

            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            print(f"Ошибка API (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)

    return None

def get_gemini_response_for_questions(prompt):
    # Твой новый ключ от ProxyAPI
    api_key = "sk-Uzay8S0pApr49nG350VVRRRNbtsks7wu"

    # URL для ProxyAPI (используем ту же модель gemma-3)
    url = "https://api.proxyapi.ru/google/v1beta/models/gemini-2.5-flash-lite:generateContent"

    # Ключ теперь передается здесь
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95
        }
    }

    max_retries = 10
    for attempt in range(max_retries):
        try:
            # Убедись, что в url больше нет ?key=...
            response = requests.post(url, headers=headers, json=payload, timeout=60)

            # Обработка лимитов и перегрузки
            if response.status_code in [429, 503]:
                time.sleep(10)
                continue

            response.raise_for_status()
            data = response.json()

            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            # Выводим ошибку для отладки
            print(f"Ошибка API (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)

    return None

def check_and_fill(vacancy_page):
    vacancy_page.set_viewport_size({'width': 1080, 'height': 1920})
    print('------------')
    try:
        # Ждем кнопку отклика
        respond_button = vacancy_page.locator('[data-qa="vacancy-response-link-top"]').first
        if respond_button.is_visible():
            title = vacancy_page.locator('[data-qa="vacancy-title"]').inner_text()

            description_locators = vacancy_page.locator('[data-qa="vacancy-description"]').all()
            # Собираем текст из каждого блока, очищаем от лишних пробелов и объединяем в одну строку
            description_parts = [loc.inner_text().strip() for loc in description_locators]
            description = "\n".join([p for p in description_parts if p])  # Оставляем только непустые части

            # Если вдруг описание пустое (защита от багов)
            if not description:
                description = "Описание вакансии не найдено"

            respond_button.click()

            time.sleep(5)

            if vacancy_page.locator('[data-qa="magritte-alert"]').is_visible() or \
                            vacancy_page.locator('.vacancy-response-popup').is_visible():

                print("Появилось предупреждение. Пытаюсь подтвердить отклик...")

                # 1. Вариант для Magritte: ищем кнопку по тексту "Всё равно откликнуться"
                confirm_btn = vacancy_page.get_by_role("button", name="Всё равно откликнуться")

                # 2. Вариант для релокации (твой старый)
                relocation_btn = vacancy_page.locator('[data-qa="relocation-warning-confirm"]')

                if confirm_btn.is_visible():
                    confirm_btn.click()
                    print("Нажато: 'Всё равно откликнуться'")
                elif relocation_btn.is_visible():
                    relocation_btn.click()
                    print("Нажато подтверждение релокации")

            time.sleep(5)

            # ТВОЙ СТАРЫЙ БЛОК ОТПРАВКИ
            if 'applicant/vacancy_response' in vacancy_page.url:
                solve_form_with_ai(vacancy_page, f"Название: {title}\nОписание: {description}")
            elif 'hh.ru/vacancy' in vacancy_page.url:

                cover_letter = get_gemini_response(f"Название: {title}\nОписание: {description}")

                if cover_letter is None or not isinstance(cover_letter, str) or cover_letter.strip() == "":
                    print(f"Пропускаю вакансию '{title}': письмо не получено (ошибка API или лимиты).")
                    return

                if vacancy_page.locator('[data-qa="chatik-root"]').is_hidden():
                    # Ждем появления текстового поля (HH иногда тупит)
                    vacancy_page.locator('[data-qa="textarea-native-wrapper"]').locator('textarea').first.fill(
                        cover_letter)

                    # Нажимаем отправить
                    if vacancy_page.locator('[data-qa="modal-overlay"]').is_visible():
                        vacancy_page.locator('[data-qa="vacancy-response-submit-popup"]').click()
                    else:
                        vacancy_page.locator('[data-qa="vacancy-response-letter-submit"]').click()
                    print(f"Откликнулись на: {title} - {vacancy_page.url}")
                else:
                    vacancy_page.locator('[data-qa="vacancy-response-link-view-topic"]').nth(1).click()
                    vacancy_page.locator('[data-qa="chatik-chat-message-applicant-action"]').click()
                    vacancy_page.locator('[data-qa="chatik-new-message-text"]').first.fill(cover_letter)
                    vacancy_page.locator('[data-qa="chatik-do-send-message"]').click()
                    print(f"Откликнулись на: {title} - {vacancy_page.url}")

            time.sleep(3)

        else:
            print(f"Уже откликнулись или кнопка недоступна: {vacancy_page.url}")
    except Exception as e:
        print(f"Ошибка внутри страницы вакансии - {vacancy_page.url} : {e}")

def solve_form_with_ai(page, vacancy_context=""):
    # 1. Собираем структуру формы
    task_blocks = page.locator('[data-qa="task-body"]').all()
    form_structure = []

    for index, block in enumerate(task_blocks):
        question_element = block.locator('[data-qa="task-question"]')
        if question_element.count() == 0: continue

        question = question_element.inner_text().strip()
        options = [opt.inner_text().strip() for opt in block.locator('[data-qa="cell-text-content"]').all()]

        # ПРОВЕРКА НА МНОЖЕСТВЕННЫЙ ВЫБОР (чекбоксы)
        is_checkbox = block.locator('input[type="checkbox"]').count() > 0

        textarea = block.locator('textarea')
        is_textarea = textarea.count() > 0 and textarea.first.is_visible()

        item = {"id": index, "question": question}
        if options:
            # Указываем тип явно, чтобы ИИ знал правила игры
            item["type"] = "multi-choice" if is_checkbox else "choice"
            item["options"] = options
        elif is_textarea:
            item["type"] = "textarea"

        form_structure.append(item)

    # 2. Единый запрос к ИИ: Анкета + Письмо
    # Мы просим ИИ проанализировать вопросы анкеты, чтобы письмо не дублировало их
    # или, наоборот, дополняло, если в анкете просят "укажите в письме..."

    prompt = f"""
    ВАКАНСИЯ: {vacancy_context}
    Промпт для сопроводительного письма {system_prompt}
    Ответы на вопросы не входят в лимит указанный выше в промпте для сопроводительного письма. Этот лимит ТОЛЬКО для сопроводительного письма
    ЗП: 80000 руб.
    
    АНКЕТА (вопросы):
    {json.dumps(form_structure, ensure_ascii=False)}

    ЗАДАЧА:
    1. Дай ответы на вопросы анкеты (answers). 
       ВАЖНО: Если вопрос типа "multi-choice", выбери все подходящие варианты и перечисли их через символ пайп "|". 
       Например: "SQL|Python/Bash"
    2. Напиши сопроводительное письмо (cover_letter).

    ВЕРНИ СТРОГО JSON:
    {{
      "answers": {{"ID_вопроса": "Текст или варианты через |"}},
      "cover_letter": "Текст письма"
    }}
    """

    raw_response = get_gemini_response_for_questions(prompt)


    if not raw_response: return

    try:
        clean_json = re.sub(r'```json|```', '', raw_response).strip()
        data = json.loads(clean_json)
        ai_answers = data.get("answers", {})
        final_letter = data.get("cover_letter", "")
    except Exception as e:
        print(f"Ошибка анализа: {e}")
        return

    print(ai_answers)

    # 3. Заполняем поля анкеты
    for index, block in enumerate(task_blocks):
        answer_raw = ai_answers.get(str(index))
        if not answer_raw: continue

        selected_answers = [a.strip().lower() for a in str(answer_raw).split('|')]

        cells = block.locator('label[data-qa="cell"]')
        textarea = block.locator('textarea')

        # Переменные для управления логикой "своего варианта"
        found_match = False
        custom_variant_cell = None

        if cells.count() > 0:
            for i in range(cells.count()):
                cell = cells.nth(i)
                txt_node = cell.locator('[data-qa="cell-text-content"]')
                input_node = cell.locator('input')

                cell_text = txt_node.inner_text().strip().lower() if txt_node.count() > 0 else ""
                val_attr = input_node.get_attribute("value") or ""

                # А) Проверяем, совпадает ли текст кнопки с ответом ИИ (обычный выбор)
                if any(ans == cell_text for ans in selected_answers):
                    cell.click()
                    found_match = True
                    # Если это радиокнопка (не чекбокс), выходим из цикла кнопок
                    if input_node.get_attribute("type") != "checkbox":
                        break

                # Б) Запоминаем кнопку "Свой вариант", если она есть в блоке
                # Ищем по ключевым словам или по значению "open" (стандарт HH для таких полей)
                if any(word in cell_text for word in ["свой", "вариант", "другое", "ваш ответ"]) or val_attr == "open":
                    custom_variant_cell = cell

            # В) Если ИИ что-то прислал, но мы не нашли точного совпадения среди кнопок
            # Значит, это значение для "Своего варианта"
            if not found_match and custom_variant_cell:
                custom_variant_cell.click()
                page.wait_for_timeout(500)  # Ждем появления textarea

        # 2. Заполнение текстового поля (textarea)
        # Оно может быть либо единственным в блоке, либо появиться после клика выше
        if textarea.count() > 0:
            if textarea.first.is_visible():
                clean_text = str(answer_raw).replace("|", ", ")
                textarea.first.fill(clean_text)

    # 4. Вставляем письмо (уже учитывающее анкету)
    try:
        letter_toggle = page.locator('[data-qa="vacancy-response-letter-toggle"]')
        if letter_toggle.is_visible():
            letter_toggle.click()

        letter_input = page.locator(
            'textarea[name="letter"], [data-qa="vacancy-response-popup-form-letter-input"]').first

        # Ждем и принудительно чистим
        letter_input.wait_for(state="visible", timeout=3000)
        letter_input.click()  # Фокус
        letter_input.fill("")  # Очистка от старого мусора HH
        letter_input.fill(final_letter.replace('\\n', '\n'))

        print("Сопроводительное письмо из JSON вставлено в анкету.")
    except Exception as e:
        print(f"Письмо не вставлено: {e}")

    # 5. Отправка
    submit_btn = page.locator('[data-qa="vacancy-response-submit-popup"]')
    if submit_btn.is_visible():
        submit_btn.click()
        print("Отклик с анкетой отправлен!")

def test_hh():
    with sync_playwright() as p:
        # Используем твой контекст
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            slow_mo=500,
            timeout=15000
        )

        # ГЛОБАЛЬНАЯ ПАМЯТЬ: Множество для хранения ID всех обработанных вакансий за сеанс
        processed_vacancies = set()

        print('\n')
        page = context.new_page()
        page.set_viewport_size({'width': 1080, 'height': 1920})

        # 1. Обновляем резюме
        page.goto('https://hh.ru/applicant/resumes')
        update_btn = page.locator('[data-qa="resume-update-button resume-update-button_actions"]')
        if update_btn.is_visible():
            update_btn.click()
            print("Резюме обновлено")

        # 2. Переходим к автопоискам
        base_url = 'https://hh.ru/applicant/autosearch.xml'
        page.goto(base_url)

        print("Начинаю поиск новых вакансий во всех автопоисках...")

        # Используем WHILE, так как кнопки "Новые вакансии" исчезают после клика
        while True:
            # Всегда берем ПЕРВУЮ видимую кнопку счетчика новых вакансий
            new_vacancy_btn = page.locator('[data-qa="autosearch__results-counter_new"]').first

            # ВОЗМОЖНЫЕ ТЕГИ
            # autosearch__results-counter_total
            # autosearch__results-counter_new

            # Если кнопок больше нет — все новые вакансии просмотрены
            if not new_vacancy_btn.is_visible():
                print("Все автопоиски с новыми вакансиями обработаны!")
                break

            try:
                # Определяем название поиска через родительскую карточку
                search_card = page.locator('[data-qa="autosearch-item"]').filter(has=new_vacancy_btn).first
                search_title = search_card.locator('[data-qa="autosearch__title"]').inner_text().strip()

                print(f"\n>>> ВХОД В АВТОПОИСК: {search_title} <<<")

                # Кликаем по кнопке (например, "56 новых вакансий")
                new_vacancy_btn.click()

                # ------

                # ДЛЯ ОБЩИХ ПОИСКОВ
                # page.wait_for_selector('[data-qa="vacancy-serp__vacancy"]', timeout=10000)
                #
                # page.locator('[data-qa="search-period-menu"]').click()
                # page.locator('[data-qa="order-by-1"]').click()

                # ------

                # Ждем загрузки результатов
                page.wait_for_selector('[data-qa="vacancy-serp__vacancy"]', timeout=10000)

                # --- БЛОК ОБРАБОТКИ ВАКАНСИЙ ---
                vacancies = page.locator('[data-qa="vacancy-serp__vacancy"]').all()

                for div in vacancies:
                    try:
                        v_title_loc = div.locator('[data-qa="serp-item__title"]')
                        e_name_loc = div.locator('[data-qa="vacancy-serp__vacancy-employer"]')

                        if v_title_loc.count() == 0:
                            continue

                        v_title = v_title_loc.inner_text().strip()
                        e_name = e_name_loc.inner_text().strip() if e_name_loc.count() > 0 else "Не указан"

                        # Создаем уникальный идентификатор вакансии
                        current_id = f"{v_title}_{e_name}"

                        # ПРОВЕРКА: Если эта вакансия уже встречалась в ЛЮБОМ из списков
                        if current_id in processed_vacancies:
                            print(f"Пропуск дубля: {v_title} ({e_name})")
                            continue

                        if div.locator('[data-qa="vacancy-serp__vacancy_response"]').is_hidden():
                            continue

                        print(f"Обработка: {v_title} в {e_name}")

                        # Открываем вакансию в новой вкладке
                        with context.expect_page() as new_page_info:
                            v_title_loc.click()

                        vacancy_page = new_page_info.value
                        vacancy_page.wait_for_load_state()

                        # Вызов вашей функции заполнения анкеты (ИИ + радиокнопки)
                        check_and_fill(vacancy_page)

                        vacancy_page.close()

                        # ДОБАВЛЯЕМ в память, что на эту вакансию мы уже откликнулись
                        processed_vacancies.add(current_id)

                        print(f"Пауза 12 сек для обхода лимитов...")
                        time.sleep(12)

                    except Exception as e:
                        print(f"Ошибка при обработке вакансии: {e}")
                        continue
                # --- КОНЕЦ БЛОКА ОБРАБОТКИ ВАКАНСИЙ ---

                # Возвращаемся в меню автопоисков (кнопка текущего поиска исчезнет, т.к. вакансии станут "просмотренными")
                print(f"<<< Завершил '{search_title}'. Возвращаюсь к списку...")
                page.goto(base_url)
                page.wait_for_load_state()

            except Exception as e:
                print(f"Ошибка при работе с автопоиском: {e}")
                page.goto(base_url)
                time.sleep(5)
                continue

        print(f"\nРабота завершена. Всего обработано уникальных вакансий: {len(processed_vacancies)}")
        context.close()