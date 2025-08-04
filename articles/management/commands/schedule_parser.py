from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
import schedule
import time
import threading
from articles.models import Article

class Command(BaseCommand):
    help = 'Запускает планировщик для автоматического парсинга статей'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Удалить все статьи перед парсингом'
        )

    def handle(self, *args, **options):
        def run_parser():
            if options.get('clear'):
                count, _ = Article.objects.all().delete()
                self.stdout.write(self.style.WARNING(f'Удалено статей: {count}'))
            self.stdout.write("Запуск автоматического парсинга...")
            try:
                call_command('main', '--limit', '50')
                self.stdout.write(self.style.SUCCESS("Парсинг завершен успешно"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка парсинга: {e}"))

        # Планируем парсинг на каждый понедельник в 9:00
        schedule.every().monday.at("09:00").do(run_parser)
        
        # Также запускаем при старте сервера
        run_parser()
        
        self.stdout.write("Планировщик запущен. Парсинг будет выполняться каждый понедельник в 9:00")
        
        # Бесконечный цикл для выполнения задач
        while True:
            schedule.run_pending()
            time.sleep(60)  # Проверяем каждую минуту