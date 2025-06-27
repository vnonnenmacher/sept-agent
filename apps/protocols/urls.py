from django.urls import path
from .views import ProtocolUploadView, ProtocolSemanticSearchView

urlpatterns = [
    path("upload/", ProtocolUploadView.as_view(), name="protocol-upload"),
    path("search/", ProtocolSemanticSearchView.as_view(), name="protocol-search"),
]
