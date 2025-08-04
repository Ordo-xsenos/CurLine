from django.core.management.base import BaseCommand
from articles.models import Article, Tag
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import time
from django.utils.text import slugify
from django.db import transaction

class Command(BaseCommand):
    help = 'Парсит статьи с towardsdatascience.com и сохраняет в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=1,
            help='Количество страниц для парсинга (по умолчанию 1)'
        )

    def handle(self, *args, **options):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
        }

        def get_article_links(base_url, pages):
            links = set()
            for page in range(1, pages + 1):
                if page == 1:
                    page_url = f"{base_url}latest/"
                else:
                    page_url = f"{base_url}latest/page/{page}/"
                try:
                    response = requests.get(page_url, headers=headers, timeout=10)
                    response.raise_for_status()
                except requests.RequestException as e:
                    self.stdout.write(f"Ошибка загрузки страницы: {page_url} - {e}")
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')
                for li in soup.find_all('li', class_='wp-block-post'):
                    if isinstance(li, Tag):
                        a = li.find('a', href=True)
                        if isinstance(a, Tag):
                            href = a.get('href')
                            if href and isinstance(href, str) and href.startswith("https://towardsdatascience.com/"):
                                links.add(href)
            return list(links)

        def get_article_content(url):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                self.stdout.write(f"Ошибка загрузки статьи: {url} - {e}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('h1')
            paragraphs = soup.find_all('p')
            content = "\n".join(p.get_text() for p in paragraphs)
            
            # Создаем slug из заголовка
            title_text = title.get_text(strip=True) if title else "No Title"
            slug = slugify(title_text)
            
            return {
                "title": title_text,
                "url": url,
                "content": content,
                "slug": slug
            }

        base_url = "https://towardsdatascience.com/"
        pages = options['pages']
        self.stdout.write(f"Собираем ссылки на статьи с {pages} страниц...")
        article_links = get_article_links(base_url, pages)
        self.stdout.write(f"Найдено {len(article_links)} статей.")

        # Удаляю limit, теперь парсим все собранные ссылки
        saved_count = 0

        for i, link in enumerate(article_links):
            self.stdout.write(f"\n[{i+1}] Загружаем статью: {link}")
            article_data = get_article_content(link)
            
            if article_data:
                # Проверяем, не существует ли уже статья с таким URL
                if not Article.objects.filter(url=article_data['url']).exists():
                    try:
                        with transaction.atomic():
                            # Создаем статью с slug
                            article = Article.objects.create(
                                title=article_data['title'],
                                url=article_data['url'],
                                content=article_data['content'],
                                slug=article_data['slug']
                            )
                            saved_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"Сохранена статья: {article.title}")
                            )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Ошибка сохранения: {e}")
                        )
                else:
                    self.stdout.write("Статья уже существует в базе данных")
            else:
                self.stdout.write("Не удалось загрузить статью.")
            
            time.sleep(2)  # 2 секунды между запросами

        self.stdout.write(
            self.style.SUCCESS(f"\nПарсинг завершен! Сохранено {saved_count} новых статей.")
        )
