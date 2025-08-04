# articles/templatetags/split_text.py

import re
from django import template
import math

register = template.Library()

@register.filter
def split_paragraphs_into_boxes(text, max_chars=400):
    """
    Разбивает текст на блоки (параграфы), каждый не длиннее max_chars символов.
    Если следующее предложение не помещается, оно начинается в новом параграфе.
    Возвращает HTML с отступом между параграфами.
    """

    # Регулярка, которая ищет предложения: все символы до ближайшей . ! или ?
    # (с учётом того, что эти знаки тоже захватываем).
    sentences = re.findall(r'[^.!?]+[.!?]?', text, flags=re.DOTALL)

    paragraphs = []
    current_paragraph = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Проверяем, влезает ли это предложение в текущий параграф
        # +1 учитывает пробел между предложениями
        if len(current_paragraph) + len(sentence) + 1 > max_chars:
            # Если не влезает, завершаем предыдущий параграф и начинаем новый
            if current_paragraph:
                paragraphs.append(current_paragraph.strip())
            current_paragraph = sentence
        else:
            # Иначе добавляем предложение в текущий параграф
            if current_paragraph:
                current_paragraph += " " + sentence
            else:
                current_paragraph = sentence

    # Добавляем «хвост» (если остался незакрытый параграф)
    if current_paragraph:
        paragraphs.append(current_paragraph.strip())

    # Теперь формируем HTML. Каждый параграф будет в своём <div> с отступом.
    # Можно добавить свои стили или Tailwind-классы для красоты.
    # Например, mb-4 — отступ снизу (margin-bottom).
    html_result = ""
    for paragraph in paragraphs:
        html_result += f'<div class="mb-4"><p>{paragraph}</p></div>\n'

    return html_result

@register.filter
def reading_time(value):
    """
    Возвращает примерное время чтения текста в минутах (минимум 1 минута).
    Скорость чтения — 250 слов в минуту.
    """
    if not isinstance(value, str):
        return "1 мин"
    words = len(value.split())
    minutes = math.ceil(words / 250) or 1
    return f"{minutes} мин чтения"
