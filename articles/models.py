from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
import stripe
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        unique_together = ['name', 'category']
        ordering = ['category', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Article(models.Model):
    title = models.CharField(max_length=200, db_index=True, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    content = models.TextField()
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    url = models.URLField(unique=True, blank=True, null=True, default=title)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    tags = models.ManyToManyField(Tag, related_name='articles')
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True)
    updated_at = models.DateTimeField(auto_now=True)  # Дата обновления

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()  # e.g. 1–5
    class Meta:
        unique_together = ('user', 'article')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    read_articles = models.ManyToManyField(Article, related_name='read_by')    

class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('article', 'user')]

class Fotochki(models.Model):
    article = models.ForeignKey("Article", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')

@receiver(pre_save, sender=Article)
def create_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)

class FavouriteProduct(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    article = models.ForeignKey(to=Article, on_delete=models.CASCADE)
    article_name = models.CharField(max_length=120)
    category = models.CharField(max_length=50)

    def __str__(self):
        return f'Избранная статья - <{self.article_name}> для пользователя - {self.user.username}'

    def save(self, *args, **kwargs):
        print("SAVE FAVOURITE", self.user, self.article)
        self.article_name = self.article.title
        self.category = str(self.article.category) if self.article.category else ''
        super().save(*args, **kwargs)

