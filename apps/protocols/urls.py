from django.urls import path
from .views import (KnowledgeDocumentDeleteView,
                    KnowledgeDocumentDownloadView,
                    KnowledgeDocumentListView,
                    ProtocolUploadView,
                    ProtocolSemanticSearchView)

urlpatterns = [
    path("upload/", ProtocolUploadView.as_view(), name="protocol-upload"),
    path("search/", ProtocolSemanticSearchView.as_view(), name="protocol-search"),

    # New endpoints
    path("documents/", KnowledgeDocumentListView.as_view(), name="document-list"),
    path("documents/<int:pk>/delete/", KnowledgeDocumentDeleteView.as_view(), name="document-delete"),
    path("documents/<int:pk>/download/", KnowledgeDocumentDownloadView.as_view(), name="document-download"),
]
