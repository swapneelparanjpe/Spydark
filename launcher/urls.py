from django.urls import path
from . import views as launcher_views

urlpatterns = [
    path('', launcher_views.home, name='crawler-home'),
    path('about/', launcher_views.about, name='crawler-about'),
]