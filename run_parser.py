#!/usr/bin/env python
import os
import sys
import django

# Добавляем путь к проекту Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CurLine.settings')
django.setup()

# Импортируем и запускаем команду
from django.core.management import call_command

if __name__ == "__main__":
    try:
        print("Запуск парсера статей...")
        call_command('main', '--limit', '50')
        print("Парсинг завершен успешно!")
    except Exception as e:
        print(f"Ошибка при парсинге: {e}") 