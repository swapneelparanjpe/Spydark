from django.urls import path
from . import views as crawler_views

urlpatterns = [
    path('welcome/', crawler_views.welcome, name='welcome'),
    path('dashboard/', crawler_views.dashboard, name='dashboard'),
    path('surface/', crawler_views.surface, name='surface'),
    path('dark/', crawler_views.dark, name='dark'),
    path('crawled/', crawler_views.crawled, name='crawled'),
]
