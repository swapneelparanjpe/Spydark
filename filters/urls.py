from django.urls import path
from . import views as filter_views

urlpatterns = [
    path('img_processing/', filter_views.img_processing, name='img_processing'),
    path('text_processing/', filter_views.text_processing, name='text_processing'),
]