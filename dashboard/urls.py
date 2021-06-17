from django.urls import path
from . import views as dashboard_views

urlpatterns = [
    path('dashboard/flag_links/', dashboard_views.flag_links, name='flag_links'),
    path('dashboard/word_cloud/', dashboard_views.word_cloud, name='word_cloud'),
    path('dashboard/active_links/', dashboard_views.active_links, name='active_links'),
    path('dashboard/link_similarity/', dashboard_views.link_similarity, name='link_similarity'),
    path('dashboard/link_tree/', dashboard_views.link_tree, name='link_tree'),
    path('dashboard/content_similarity/', dashboard_views.content_similarity, name='content_similarity'),
    path('dashboard/activity_period/', dashboard_views.activity_period, name='activity_period'),
]