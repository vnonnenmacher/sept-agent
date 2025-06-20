from django.urls import path
from .views import QdrantSearchView

urlpatterns = [
    path('search/', QdrantSearchView.as_view(), name='qdrant-search'),
]
