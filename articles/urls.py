from django.urls import path
from .views import home, article_detail, search_articles, article_detail_by_id,favourites,add_favourite,delete_favourite, toggle_like

app_name = 'articles'

urlpatterns = [
    path('', home, name='home'),
    path('search/', search_articles, name='search_articles'),
    path("articles/<str:slug>/", article_detail, name="article_detail"),
    path("article/<int:article_id>/", article_detail_by_id, name="article_detail_by_id"),
    path('favourites/', favourites, name='favourites'),
    path('favorites/add/<int:product_id>/', add_favourite, name='add_favourite'),
    path('favorite/remove/<int:product_id>/', delete_favourite, name='delete_favourite'),
    path('like/', toggle_like, name='toggle_like'),
]
