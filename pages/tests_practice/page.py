from pynput.keyboard import Key, Controller
import re
import random
import numpy as np
import math
import time

import config
from pages.base.page import BasePage
from services.ai.ai_service import ServiceAi
from pages.tests_practice.locators import TestPracticeLocators

class TestPracticePage(BasePage):
    class BiometricTypist:
        """
        Эмуляция человеческой печати с Keystroke Dynamics.
        Учитывает анатомию пальцев, усталость, джиттер и контекстные паузы.
        """

        def __init__(self):
            # Профили пальцев (dwell time в мс)
            self.dwell_times = {
                'pinky': {'base': 120, 'sigma': 25,
                          'keys': ['q', 'a', 'z', 'p', ';', '/', '1', '0', '\t', '\n', Key.tab, Key.enter,
                                   Key.backspace]},
                'ring': {'base': 110, 'sigma': 20, 'keys': ['w', 's', 'x', 'o', 'l', '.', '2', '9']},
                'middle': {'base': 95, 'sigma': 18, 'keys': ['e', 'd', 'c', 'i', 'k', ',', '3', '8']},
                'index': {'base': 85, 'sigma': 15,
                          'keys': ['r', 'f', 'v', 't', 'g', 'b', 'y', 'h', 'n', 'u', 'j', 'm', '4', '5', '6', '7']},
                'thumb': {'base': 100, 'sigma': 20, 'keys': [' ', Key.space]}
            }

            self.flight_time_cache = {}
            self.fatigue = 0.0
            self.char_count = 0
            self.key_history = []
            self.typo_count = 0  # счетчик опечаток для реалистичности

        def get_finger(self, char_or_key):
            """Определяем палец для символа или клавиши"""
            if isinstance(char_or_key, Key):
                # Для специальных клавиш
                if char_or_key in (Key.enter, Key.backspace):
                    return 'pinky'
                elif char_or_key == Key.space:
                    return 'thumb'
                elif char_or_key == Key.tab:
                    return 'pinky'
                return 'index'

            char = str(char_or_key).lower()
            for finger_name, finger_data in self.dwell_times.items():
                if char in finger_data['keys']:
                    return finger_name
            return 'index'

        def gaussian_dwell(self, finger, char_or_key):
            """Реалистичное время удержания клавиши с эффектом усталости"""
            base = self.dwell_times[finger]['base']
            sigma = self.dwell_times[finger]['sigma']

            # Усталость увеличивает dwell time на 0-30%
            fatigue_factor = 1 + (self.fatigue * 0.3)

            # Логнормальное распределение (более реалистично, чем нормальное)
            mu = math.log(max(1, base * fatigue_factor))
            sigma_log = sigma / max(1, base)

            dwell = np.random.lognormal(mu, sigma_log) / 1000.0  # в секунды
            return max(0.02, min(dwell, 0.3))

        def get_flight_time(self, from_char, to_char, context=""):
            """Реалистичное время перехода между клавишами"""
            cache_key = f"{from_char}_{to_char}"
            if cache_key in self.flight_time_cache:
                return self.flight_time_cache[cache_key] * random.uniform(0.92, 1.08)

            base_flight = 0.06  # 60ms базовая задержка

            from_finger = self.get_finger(from_char)
            to_finger = self.get_finger(to_char)

            # Тот же палец — медленнее
            if from_finger == to_finger:
                base_flight *= 2.2
            # Соседние пальцы — быстрее
            elif (from_finger == 'index' and to_finger == 'middle') or \
                    (from_finger == 'middle' and to_finger == 'index') or \
                    (from_finger == 'middle' and to_finger == 'ring') or \
                    (from_finger == 'ring' and to_finger == 'middle'):
                base_flight *= 0.75

            # Частые биграммы печатаются быстрее
            common_bigrams = ['th', 'he', 'in', 'er', 'an', 're', 'nd', 'at', 'on', 'nt', 'ha', 'es', 'st', 'en', 'ed',
                              'or', 'to', 'it', 'is', 'ng']
            bigram = f"{str(from_char).lower()}{str(to_char).lower()}"
            if bigram in common_bigrams:
                base_flight *= 0.55

            # Джиттер
            jitter = random.gauss(0, 0.012)

            flight_time = max(0.015, base_flight + jitter)
            self.flight_time_cache[cache_key] = flight_time

            return flight_time

        def update_fatigue(self, char_or_key):
            """Обновляем уровень усталости"""
            self.char_count += 1
            self.key_history.append(str(char_or_key))

            if len(self.key_history) > 60:
                self.key_history.pop(0)

            # Нелинейный рост усталости
            self.fatigue = min(1.0, (self.char_count ** 0.65) / 180)

            # Микропаузы снижают усталость
            if random.random() < 0.04:
                self.fatigue *= 0.75

        def need_micropause(self, char):
            """Определяем необходимость паузы на обдумывание"""
            # Пауза каждые 40-80 символов
            if self.char_count > 0 and self.char_count % random.randint(40, 80) == 0:
                return random.uniform(0.8, 3.5)

            # После исправления ошибки
            if len(self.key_history) >= 3:
                last_three = ''.join(self.key_history[-3:])
                if 'Key.backspace' in last_three:
                    return random.uniform(0.4, 1.8)

            # Перед сложными конструкциями (скобки, кавычки)
            if char in '([{"""':
                if random.random() < 0.3:
                    return random.uniform(0.2, 0.8)

            return 0

        def human_typo(self, char):
            """Генерируем реалистичную опечатку (3% шанс)"""
            if random.random() > 0.03:
                return None

            adjacent_keys = {
                'a': 's', 's': 'a', 'd': 'f', 'f': 'd', 'g': 'h', 'h': 'g',
                'j': 'k', 'k': 'j', 'l': ';', ';': 'l',
                'q': 'w', 'w': 'q', 'e': 'r', 'r': 'e', 't': 'y', 'y': 't',
                'u': 'i', 'i': 'u', 'o': 'p', 'p': 'o',
                'z': 'x', 'x': 'z', 'c': 'v', 'v': 'c', 'b': 'n', 'n': 'b',
                '1': '2', '2': '1', '3': '4', '4': '3',
            }

            typo_type = random.choice(['adjacent', 'double', 'skip'])

            if typo_type == 'adjacent' and char.lower() in adjacent_keys:
                wrong_char = adjacent_keys[char.lower()]
                return wrong_char.upper() if char.isupper() else wrong_char
            elif typo_type == 'double':
                return char + char
            elif typo_type == 'skip':
                return '\x00'  # маркер пропуска

            return None

        def human_keystroke(self, keyboard, char):
            """
            Одно полностью реалистичное нажатие клавиши
            с биометрической динамикой и возможными ошибками
            """
            # Микропауза перед сложным действием
            micropause = self.need_micropause(char)
            if micropause > 0:
                time.sleep(micropause)

            # Обработка опечатки
            typo = self.human_typo(char)
            if typo and typo != '\x00':
                # Печатаем неправильный символ
                wrong_finger = self.get_finger(typo)
                wrong_dwell = self.gaussian_dwell(wrong_finger, typo)

                if len(typo) == 2:  # double typo
                    keyboard.press(typo[0])
                    time.sleep(wrong_dwell)
                    keyboard.release(typo[0])
                    time.sleep(random.uniform(0.03, 0.08))
                    keyboard.press(typo[1])
                    time.sleep(wrong_dwell)
                    keyboard.release(typo[1])
                else:
                    keyboard.press(typo)
                    time.sleep(wrong_dwell)
                    keyboard.release(typo)

                # Время на осознание ошибки
                time.sleep(random.uniform(0.18, 0.5))

                # Исправление - backspace
                for _ in range(len(typo)):
                    keyboard.press(Key.backspace)
                    time.sleep(self.gaussian_dwell('pinky', Key.backspace))
                    keyboard.release(Key.backspace)
                    time.sleep(random.uniform(0.05, 0.12))

                self.typo_count += 1
                time.sleep(random.uniform(0.1, 0.35))

            # Правильное нажатие
            finger = self.get_finger(char)
            dwell_time = self.gaussian_dwell(finger, char)

            if char == '\n':
                keyboard.press(Key.space)
                keyboard.press(Key.enter)
                time.sleep(dwell_time)
                keyboard.release(Key.space)
                keyboard.release(Key.enter)
            elif char == '\t':
                keyboard.press(Key.tab)
                time.sleep(dwell_time)
                keyboard.release(Key.tab)
            elif char == ' ':
                keyboard.press(Key.space)
                time.sleep(dwell_time)
                keyboard.release(Key.space)
            else:
                keyboard.press(char)
                time.sleep(dwell_time)
                keyboard.release(char)

            self.update_fatigue(char)
            return dwell_time

    def enhance_isTrusted_compatibility(self):
        """
        Дополнительные трюки для обхода проверки isTrusted
        """
        # 1. Создаем "реалистичный" фокус через нативные события
        self.page.evaluate("""
            const editor = document.querySelector('.monaco-editor');
            if (editor) {
                const rect = editor.getBoundingClientRect();
                const events = ['mouseenter', 'mouseover', 'mousemove', 'mousedown', 'mouseup', 'click'];
                events.forEach(eventType => {
                    const event = new MouseEvent(eventType, {
                        bubbles: true,
                        cancelable: true,
                        clientX: rect.left + Math.random() * rect.width,
                        clientY: rect.top + Math.random() * rect.height,
                        button: 0
                    });
                    editor.dispatchEvent(event);
                });

                // Дополнительно: триггерим фокус на textarea внутри Monaco
                const textarea = editor.querySelector('textarea');
                if (textarea) {
                    textarea.focus();
                    // Эмулируем реальное событие фокуса
                    const focusEvent = new FocusEvent('focus', {
                        bubbles: true,
                        cancelable: true,
                        relatedTarget: document.body
                    });
                    textarea.dispatchEvent(focusEvent);
                }
            }
        """)

        # 2. Физические клики мыши по редактору со случайным смещением
        editor_rect = self.page.locator(TestPracticeLocators.MONACO_EDITOR).bounding_box()
        if editor_rect:
            for _ in range(random.randint(1, 3)):
                x = editor_rect['x'] + random.randint(50, int(editor_rect['width'] - 50))
                y = editor_rect['y'] + random.randint(20, int(editor_rect['height'] - 20))
                self.page.mouse.click(x, y)
                time.sleep(random.uniform(0.1, 0.3))

            # Иногда делаем "двойной клик" для выделения слова (как человек)
            if random.random() < 0.3:
                x = editor_rect['x'] + random.randint(100, int(editor_rect['width'] - 100))
                y = editor_rect['y'] + random.randint(30, int(editor_rect['height'] - 30))
                self.page.mouse.dblclick(x, y)
                time.sleep(random.uniform(0.2, 0.4))
                # Кликаем еще раз чтобы снять выделение
                self.page.mouse.click(
                    editor_rect['x'] + random.randint(10, 50),
                    editor_rect['y'] + random.randint(5, 15)
                )
                time.sleep(random.uniform(0.1, 0.2))

    def human_type_code(self, solution_code, brackets=None, quotes=None):
        """
        Печать кода с полной эмуляцией человеческого поведения,
        включая обход автозакрытия Monaco Editor и проверки isTrusted.
        """
        if brackets is None:
            brackets = {'(': ')', '[': ']', '{': '}'}
        if quotes is None:
            quotes = {'"': '"', "'": "'"}

        biometric = self.BiometricTypist()
        keyboard = Controller()

        # Сбрасываем все модификаторы
        for k in [Key.cmd, Key.shift, Key.alt, Key.ctrl]:
            keyboard.release(k)

        print(f"🧑‍💻 Начинаю человеческий ввод ({len(solution_code)} симв.)...")

        # ===== ВАЖНО: Эмуляция человеческого фокуса перед вводом =====
        self.enhance_isTrusted_compatibility()
        time.sleep(random.uniform(0.3, 0.6))

        # Дополнительно: "человеческий" клик по редактору
        editor_overlay = self.page.locator(TestPracticeLocators.MONACO_EDITOR).first
        box = editor_overlay.bounding_box()
        if box:
            # Первый клик — "промах" мимо центра
            click_x = box['x'] + box['width'] * random.uniform(0.2, 0.45)
            click_y = box['y'] + box['height'] * random.uniform(0.4, 0.6)
            self.page.mouse.click(click_x, click_y)
            time.sleep(random.uniform(0.15, 0.3))

            # Второй клик — уже ближе к нужному месту
            click_x = box['x'] + box['width'] * random.uniform(0.35, 0.65)
            click_y = box['y'] + box['height'] * random.uniform(0.3, 0.55)
            self.page.mouse.click(click_x, click_y)
            time.sleep(random.uniform(0.2, 0.4))

        skip_next_char = None
        prev_char = None

        for idx, char in enumerate(solution_code):
            # --- ОБХОД АВТОЗАКРЫТИЯ: перешагиваем авто-пару ---
            if char == skip_next_char:
                time.sleep(biometric.get_flight_time(prev_char or ' ', Key.right))
                keyboard.press(Key.right)
                time.sleep(biometric.gaussian_dwell('pinky', Key.right))
                keyboard.release(Key.right)
                skip_next_char = None
                prev_char = Key.right
                biometric.update_fatigue(Key.right)
                continue

            # --- Flight time перед символом ---
            if prev_char is not None:
                flight = biometric.get_flight_time(prev_char, char)
                time.sleep(flight)

            # --- ПЕЧАТЬ СИМВОЛА С БИОМЕТРИЕЙ ---
            biometric.human_keystroke(keyboard, char)
            prev_char = char

            # --- ЛОГИКА ПОСЛЕ ПЕЧАТИ (Monaco автозаполнение) ---

            # Запоминаем кавычку для перешагивания
            if char in quotes:
                skip_next_char = quotes[char]
            else:
                skip_next_char = None

            # Удаляем авто-закрывающуюся скобку
            if char in brackets:
                time.sleep(random.uniform(0.04, 0.08))

                keyboard.press(Key.right)
                time.sleep(biometric.gaussian_dwell('pinky', Key.right))
                keyboard.release(Key.right)

                time.sleep(random.uniform(0.03, 0.06))

                keyboard.press(Key.backspace)
                time.sleep(biometric.gaussian_dwell('pinky', Key.backspace))
                keyboard.release(Key.backspace)

                prev_char = Key.backspace
                biometric.update_fatigue(Key.backspace)

            # Микро-пауза между символами
            time.sleep(random.uniform(0.02, 0.06))

            # Периодически обновляем isTrusted через микродвижения мыши
            if idx % random.randint(30, 60) == 0:
                current_box = editor_overlay.bounding_box()
                if current_box:
                    # Легкое движение мыши (как будто следим за курсором)
                    mx = current_box['x'] + current_box['width'] * random.uniform(0.3, 0.7)
                    my = current_box['y'] + current_box['height'] * random.uniform(0.1, 0.3)
                    self.page.mouse.move(mx, my)
                    time.sleep(random.uniform(0.05, 0.15))

        print(f"✅ Человеческий ввод завершен. Опечаток исправлено: {biometric.typo_count}")

    def solve_test_practice(self, skill_name, mode):
        print(f"🛠 Работаю над практической задачей по {skill_name}...")

        time.sleep(5)

        max_attempts = 10
        attempt = 1
        last_error = ""

        # 1. Сбор описания задачи
        try:
            self.page.wait_for_selector(TestPracticeLocators.MAIN_CONTAINER, timeout=15000)
        except:
            if "applicant/contest_result" in self.page.url:
                return "FINISH"
            return "ERROR"

        while attempt <= max_attempts:
            print(f"🔄 Попытка {attempt} из {max_attempts}...")

            self.page.wait_for_timeout(1000)

            elements = self.page.locator(TestPracticeLocators.MAIN_CONTAINER).all()

            description_text = ""
            current_code = ""
            error_report = ""

            if len(elements) >= 3:
                description_text = elements[0].inner_text().strip()

                elements[1].scroll_into_view_if_needed()
                line_locators = elements[1].locator(TestPracticeLocators.CODE_LINES).all()

                if not line_locators:
                    self.page.wait_for_timeout(1000)
                    line_locators = elements[1].locator(TestPracticeLocators.CODE_LINES).all()

                code_lines = [line.inner_text().replace('\u00a0', ' ') for line in line_locators]
                current_code = "\n".join(code_lines)

                error_report = elements[2].inner_text().strip()

            task_text = f"ОПИСАНИЕ ЗАДАЧИ:\n{description_text}\n\n"
            task_text += f"ТЕКУЩИЙ КОД В РЕДАКТОРЕ:\n{current_code}\n\n"
            task_text += f"ОШИБКИ И ТЕСТЫ:\n{error_report}"

            # 2. Формируем промпт
            if attempt == 1:
                prompt = f"Напиши код решения для задачи по {skill_name}.{task_text}ВЕРНИ ТОЛЬКО ЧИСТЫЙ КОД. Обязательно используй начальную структуру"
            else:
                prompt = f"Предыдущий код не прошел тесты. Исправь его. Не повторяй предыдущий код. {task_text}ВЕРНИ ТОЛЬКО ИСПРАВЛЕННЫЙ ЧИСТЫЙ КОД."

            # 3. Получаем ответ от ИИ
            solution_code = ServiceAi.get_gemini_response_for_practice(prompt)
            if solution_code is None:
                print(f"❌ ИИ не вернул ответ. Повторяю...")
                attempt += 1
                continue

            # 3.1 Очистка кода от маркдауна и мыслей
            if "<|thought|>" in solution_code:
                solution_code = solution_code.split("</|thought|>")[-1]

            for lang in ["cpp", "python", "javascript", "php", "sql", "go", "java", "csharp", "typescript", "kotlin",
                         "swift", "rust", "ruby"]:
                solution_code = solution_code.replace(f"```{lang}", "")
            solution_code = solution_code.replace("```", "").strip()

            # Функция для безопасного удаления комментариев
            def safe_clean_comments(text, lang_name):
                """
                Удаляет комментарии из кода, сохраняя строки в кавычках.
                Поддерживает все популярные языки программирования.
                """
                # Паттерн для строк в кавычках (их не трогаем)
                string_pattern = r'''
                        (?:
                            "(?:[^"\\]|\\.)*"           # Двойные кавычки
                            |'(?:[^'\\]|\\.)*'           # Одинарные кавычки
                            |`(?:[^`\\]|\\.)*`           # Бэктики (шаблонные строки)
                            |\"\"\"[\s\S]*?\"\"\"        # Тройные двойные кавычки (Python)
                            |\'\'\'[\s\S]*?\'\'\'        # Тройные одинарные кавычки (Python)
                        )
                    '''

                def replace_func(match):
                    item = match.group(0)
                    # Если это строка в кавычках — возвращаем как есть
                    if item and (item[0] in ('"', "'", '`')):
                        return item
                    return ""  # комментарий удаляем

                # Определяем паттерны комментариев в зависимости от языка
                lang_lower = lang_name.lower()

                # Комментарии для разных языков
                single_line_comments = []
                multi_line_comments = []

                # Python, Ruby, Shell, YAML, Perl
                if lang_lower in ['python', 'ruby', 'shell', 'bash', 'yaml', 'perl', 'r']:
                    single_line_comments.append(r'#.*')
                # SQL, Lua, Haskell, Ada
                elif lang_lower in ['sql', 'postgresql', 'mysql', 'lua', 'haskell', 'ada']:
                    single_line_comments.append(r'--.*')
                # MATLAB, Octave
                elif lang_lower in ['matlab', 'octave']:
                    single_line_comments.append(r'%.*')
                # C-style языки (Java, C++, C#, JavaScript, Go, Rust, Swift, Kotlin, PHP, TypeScript, Dart, Scala)
                elif lang_lower in ['java', 'c++', 'cpp', 'c#', 'csharp', 'javascript', 'js', 'go', 'golang',
                                    'rust', 'swift', 'kotlin', 'php', 'typescript', 'dart', 'scala', 'c',
                                    'objective-c', 'objc', 'groovy', 'solidity']:
                    single_line_comments.append(r'//.*')
                    multi_line_comments.append(r'/\*[\s\S]*?\*/')

                # По умолчанию пробуем все паттерны (для неизвестных языков)
                if not single_line_comments and not multi_line_comments:
                    single_line_comments = [r'#.*', r'--.*', r'//.*']
                    multi_line_comments = [r'/\*[\s\S]*?\*/']

                # Собираем все паттерны комментариев
                all_comment_patterns = []
                if single_line_comments:
                    all_comment_patterns.append('|'.join(f'({p})' for p in single_line_comments))
                if multi_line_comments:
                    all_comment_patterns.append('|'.join(f'({p})' for p in multi_line_comments))

                if not all_comment_patterns:
                    return text  # нет паттернов — возвращаем как есть

                comment_pattern = '|'.join(all_comment_patterns)

                # Итоговый паттерн: строки + комментарии
                # Используем verbose mode для читаемости
                full_pattern = f'(?:{string_pattern})|(?:{comment_pattern})'

                try:
                    # Компилируем с флагами VERBOSE и DOTALL
                    compiled_pattern = re.compile(full_pattern, re.VERBOSE | re.DOTALL)

                    # Обрабатываем построчно, чтобы сохранить структуру отступов
                    lines = text.split('\n')
                    cleaned_lines = []

                    for line in lines:
                        # Удаляем комментарии в строке
                        cleaned_line = compiled_pattern.sub(replace_func, line)
                        # Убираем trailing пробелы после удаления комментариев
                        cleaned_line = cleaned_line.rstrip()
                        cleaned_lines.append(cleaned_line)

                    result = '\n'.join(cleaned_lines)

                    # Удаляем пустые строки в начале и конце
                    result = result.strip()

                    # Удаляем строки, которые стали полностью пустыми ПОСЛЕ удаления комментариев
                    # НО только если они не между блоками кода (сохраняем одиночные пустые строки)
                    final_lines = []
                    prev_empty = False
                    for line in result.split('\n'):
                        is_empty = not line.strip()
                        if is_empty and prev_empty:
                            continue  # пропускаем двойные пустые строки
                        final_lines.append(line)
                        prev_empty = is_empty

                    return '\n'.join(final_lines)

                except Exception as e:
                    print(f"⚠️ Ошибка при очистке комментариев: {e}")
                    return text

            # Определяем текущий язык
            current_lang = skill_name.lower()

            # Очищаем комментарии
            solution_code = safe_clean_comments(solution_code, current_lang)

            # Удаляем начальные пробелы в каждой строке НО сохраняем относительные отступы
            lines = solution_code.split('\n')
            if lines:
                # Находим минимальный отступ (игнорируя пустые строки)
                non_empty_lines = [line for line in lines if line.strip()]
                if non_empty_lines:
                    min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
                    # Удаляем минимальный отступ из всех строк
                    cleaned_lines = []
                    for line in lines:
                        if line.strip():
                            # Удаляем только общий минимальный отступ
                            cleaned_lines.append(line[min_indent:])
                        else:
                            cleaned_lines.append(line)
                    solution_code = '\n'.join(cleaned_lines)
                else:
                    solution_code = '\n'.join(lines)

            # Финальная очистка: удаляем пустые строки в начале и конце
            solution_code = solution_code.strip()

            print("✨ Код очищен (комментарии удалены, отступы нормализованы, структура сохранена).")

            # ==========================================
            # 4. ЧЕЛОВЕЧЕСКИЙ ВВОД КОДА
            # ==========================================
            print("⌨️ Подготавливаю редактор...")

            keyboard = Controller()
            self.page.bring_to_front()

            # ВАЖНО: сначала эмулируем человеческий фокус
            self.enhance_isTrusted_compatibility()
            time.sleep(random.uniform(0.3, 0.5))

            # Затем очищаем редактор
            print("🧹 Очищаю старый код...")
            if config.OS == 'Mac':
                with keyboard.pressed(Key.cmd):
                    time.sleep(random.uniform(0.05, 0.12))
                    keyboard.press('a')
                    time.sleep(random.uniform(0.04, 0.1))
                    keyboard.release('a')
            elif config.OS == 'Win':
                with keyboard.pressed(Key.ctrl):
                    time.sleep(random.uniform(0.05, 0.12))
                    keyboard.press('a')
                    time.sleep(random.uniform(0.04, 0.1))
                    keyboard.release('a')
            else:
                print("OS в конфиге указана неверно")
                return False

            time.sleep(random.uniform(0.15, 0.3))
            keyboard.press(Key.backspace)
            time.sleep(random.uniform(0.08, 0.15))
            keyboard.release(Key.backspace)
            time.sleep(random.uniform(0.3, 0.6))

            # Запускаем человеческий ввод (внутри уже есть enhance_isTrusted_compatibility)
            self.human_type_code(solution_code)

            # ==========================================
            # 5. Запуск тестов
            # ==========================================
            print("🧪 Запускаю тесты...")
            self.page.locator(TestPracticeLocators.EXECUTE_BTN).click()
            self.page.wait_for_timeout(6000)

            # 6. ПРОВЕРКА РЕЗУЛЬТАТОВ
            test_chips = self.page.locator(TestPracticeLocators.TEST_CHIPS).all()
            all_tests_passed = True
            error_report = ""

            # Проверка для SQL
            sql_actual_locator = self.page.locator(TestPracticeLocators.SQL_ACTUAL)
            sql_expected_locator = self.page.locator(TestPracticeLocators.SQL_EXPECTED)
            sql_error_locator = self.page.locator(TestPracticeLocators.SQL_ERROR)

            if sql_error_locator.is_visible():
                all_tests_passed = False
                error_report = f"SQL SYNTAX ERROR: {sql_error_locator.inner_text().strip()}"
            elif sql_actual_locator.is_visible() and sql_expected_locator.is_visible():
                mismatch_indicator = self.page.locator(TestPracticeLocators.MISMATCH_CHIP)
                if mismatch_indicator.is_visible():
                    all_tests_passed = False
                    actual_data = sql_actual_locator.inner_text().strip()
                    expected_data = sql_expected_locator.inner_text().strip()
                    error_report = (
                        f"SQL RESULT MISMATCH!\n"
                        f"--- ВАШ РЕЗУЛЬТАТ ---\n{actual_data}\n"
                        f"--- ОЖИДАЕМЫЙ РЕЗУЛЬТАТ ---\n{expected_data}\n"
                        f"Внимательно проверь порядок строк (ORDER BY) и точность значений."
                    )
            elif test_chips:
                chips_to_check = test_chips[:3]
                for index, chip in enumerate(chips_to_check):
                    chip.click()
                    self.page.wait_for_timeout(600)

                    expected = self.page.locator(TestPracticeLocators.EXPECTED_DATA).inner_text().strip()
                    actual = self.page.locator(TestPracticeLocators.ACTUAL_DATA).inner_text().strip()
                    has_error_icon = chip.locator(TestPracticeLocators.ERROR_ICON_CSS).count() > 0

                    if expected != actual or has_error_icon:
                        all_tests_passed = False
                        error_report += f"\nОШИБКА В ТЕСТЕ {index + 1}:\nОжидалось: {expected}\nПолучено: {actual}\n"
                        break
            elif self.page.locator(TestPracticeLocators.ACTUAL_DATA).first.is_visible():
                res_locator = self.page.locator(TestPracticeLocators.ACTUAL_DATA).first
                res_text = res_locator.inner_text()
                if any(x in res_text.lower() for x in ["error", "exception", "expected", "не совпадает"]):
                    all_tests_passed = False
                    error_report = res_text

            if all_tests_passed:
                print("✅ Все тесты пройдены!")
                submit_btn = self.page.locator(TestPracticeLocators.SUBMIT_SOLUTION_BTN)
                if submit_btn.is_enabled():
                    print("➡️ Нажимаю 'Отправить решение'...")
                    submit_btn.click()

                    if mode == config.Mode.TRAINING:
                        self.page.locator(TestPracticeLocators.FINISH_TRAINING_BTN).click()

                    self.page.wait_for_timeout(4000)

                    if "assessment.hh.ru/code" in self.page.url:
                        return "CONTINUE"
                    if "applicant/contest_result" in self.page.url:
                        return "FINISH"

                    self.page.wait_for_timeout(2000)
                    if "applicant/contest_result" in self.page.url:
                        return "FINISH"

                    return "FINISH"
            else:
                last_error = error_report
                attempt += 1
                continue

        print("⚠️ Попытки исчерпаны.")
        return "ERROR"