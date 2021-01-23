"""FYP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', include('crawler.urls')),
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('welcome/', user_views.welcome, name='welcome'),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('surface/', user_views.surface, name='surface'),
    path('deep/', user_views.deep, name='deep'),
    path('dark/', user_views.dark, name='dark'),
    path('crawled/', user_views.crawled, name='crawled'),
    path('img_processing/', user_views.img_processing, name='img_processing'),
    path('text_processing/', user_views.text_processing, name='text_processing'),
    path('dashboard/active_links/', user_views.active_links, name='active_links'),
    path('dashboard/link_tree/', user_views.link_tree, name='link_tree'),
    path('dashboard/word_cloud/', user_views.word_cloud, name='word_cloud'),
]
urlpatterns += staticfiles_urlpatterns()