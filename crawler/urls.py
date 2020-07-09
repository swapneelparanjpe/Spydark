from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='crawler-home'),
    path('about/', views.about, name='crawler-about'),
]
