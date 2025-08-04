from django.shortcuts import render, get_object_or_404, redirect
from .models import Article
from .templatetags.split_text import split_paragraphs_into_boxes
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import FavouriteProduct, Subcategory
from django.http import JsonResponse

def get_articles_or_none():
    articles = Article.objects.all().order_by('-published_at')
    return articles if articles.exists() else None


def home(request):
    articles = get_articles_or_none()
    if not articles:
        return render(request, 'index.html', {'articles': [], 'page_obj': None, 'user_likes': [], 'user_favourites': []})
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    user_likes = []
    user_favourites = []
    if request.user.is_authenticated:
        user_likes = list(request.user.liked_articles.values_list('id', flat=True))
        user_favourites = list(FavouriteProduct.objects.filter(user=request.user).values_list('article_id', flat=True))
    return render(request, 'index.html', {
        'articles': page_obj,
        'page_obj': page_obj,
        'user_likes': user_likes,
        'user_favourites': user_favourites
    })

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    processed_content = split_paragraphs_into_boxes(article.content, max_chars=400)
    return render(request, "articles_detail.html", {
        "article": article,
        "processed_content": processed_content
    })

def article_detail_by_id(request, article_id):
    """Fallback для статей без slug - переход по ID"""
    article = get_object_or_404(Article, id=article_id)
    processed_content = split_paragraphs_into_boxes(article.content, max_chars=400)
    return render(request, "article_detail.html", {
        "article": article,
        "processed_content": processed_content
    })

def search_articles(request):
    query = request.GET.get('q', '')
    if query:
        results = Article.objects.filter(title__icontains=query)
        if results.count() == 0:
            # Если статья не найдена, перенаправляем на главную страницу
            return redirect('articles:home')
        elif results.count() == 1:
            # Если найдена ровно одна статья, перенаправляем на её страницу
            article = results.first()
            return redirect('articles:article_detail', slug=article.slug)#type: ignore
        else:
            # Если найдено несколько, отображаем результаты поиска
            context = {
                'query': query,
                'results': results,
            }
            return render(request, "articles/search_results.html", context)
    else:
        # Если запрос пустой, перенаправляем на главную
        return redirect('articles:home')


@login_required
def favourites(request):
    favourites_products = FavouriteProduct.objects.filter(user=request.user)
    subcategories = Subcategory.objects.all()
    user_likes = list(request.user.liked_articles.values_list('id', flat=True))
    user_favourites = list(FavouriteProduct.objects.filter(user=request.user).values_list('article_id', flat=True))
    context = {
        'title': 'Favourites',
        'products': favourites_products,
        'subcategories': subcategories,
        'user_likes': user_likes,
        'user_favourites': user_favourites
    }
    return render(request, 'favourites.html', context)


@login_required
def add_favourite(request, product_id):
    print('CALL ADD_FAVOURITE')
    article = get_object_or_404(Article, id=product_id)
    favourite, created = FavouriteProduct.objects.get_or_create(
        user=request.user,
        article=article,
        article_name=article.title,
        category=str(article.category) if article.category else ''
    )
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'created': created})
    if created:
        messages.success(request, f'Статья "{article.title}" добавлена в избранное!')
    else:
        messages.info(request, f'Статья "{article.title}" уже находится в избранном!')
    return redirect('articles:favourites')


@login_required
def delete_favourite(request, product_id):
    product = FavouriteProduct.objects.get(id=product_id)
    product.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def toggle_like(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        article = get_object_or_404(Article, id=article_id)
        user = request.user
        liked = False
        if user in article.likes.all():
            article.likes.remove(user)
        else:
            article.likes.add(user)
            liked = True
        return JsonResponse({
            'likes_count': article.likes.count(),
            'liked': liked
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)
