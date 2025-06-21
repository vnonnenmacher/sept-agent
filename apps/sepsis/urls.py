# apps/sepsis/urls.py

from django.urls import path
from .views import SepsisEpisodeDetailView, SepsisEpisodeListView

urlpatterns = [
    path('episodes/', SepsisEpisodeListView.as_view(), name='sepsis-episode-list'),
    path('episodes/<int:id>/', SepsisEpisodeDetailView.as_view(), name='sepsis-episode-detail'),
]
