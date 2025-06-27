from django.urls import path
from .views import (
    SuggestAntibioticView,
    SuggestNextStepView,
    SuggestCCIHSuggestionsView,
)

urlpatterns = [
    path("suggest-antibiotic/", SuggestAntibioticView.as_view(), name="suggest-antibiotic"),
    path("next-step/", SuggestNextStepView.as_view(), name="suggest-next-step"),
    path("ccih-suggestions/", SuggestCCIHSuggestionsView.as_view(), name="ccih-suggestions"),
]
