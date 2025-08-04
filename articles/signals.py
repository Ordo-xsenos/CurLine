from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command
from django.apps import apps
import threading
import time

@receiver(post_migrate)
def run_parser_on_startup(sender, **kwargs):
    """Запускает парсер при старте сервера"""
    if sender.name == 'articles':
        def delayed_parser():
            time.sleep(10)  # Ждем 10 секунд после запуска сервера
            try:
                call_command('main', '--limit', '20')
                print("Автоматический парсинг завершен")
            except Exception as e:
                print(f"Ошибка автоматического парсинга: {e}")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=delayed_parser)
        thread.daemon = True
        thread.start()