from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SuggestAntibioticView,
    SuggestNextStepView,
    SuggestCCIHSuggestionsView,
    TagViewSet,
    DocumentChunkViewSet,
    TagConditionUpdateView,
)

router = DefaultRouter()
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"chunks", DocumentChunkViewSet, basename="chunk")

urlpatterns = [
    path("", include(router.urls)),
    path("suggest-antibiotic/", SuggestAntibioticView.as_view(), name="suggest-antibiotic"),
    path("suggest-next-step/", SuggestNextStepView.as_view(), name="suggest-next-step"),
    path("suggest-ccih/", SuggestCCIHSuggestionsView.as_view(), name="suggest-ccih"),
    path("tag-conditions/<int:pk>/", TagConditionUpdateView.as_view(), name="tag-condition-update"),
]
