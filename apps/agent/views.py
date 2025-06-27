from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .core import (
    define_antibiotic,
    define_next_step,
    suggest_ccih_recommendations,
)


class SuggestAntibioticView(APIView):
    def post(self, request):
        patient_context = request.data
        try:
            result = define_antibiotic(patient_context)
            return Response({"result": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SuggestNextStepView(APIView):
    def post(self, request):
        patient_context = request.data
        try:
            result = define_next_step(patient_context)
            return Response({"result": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SuggestCCIHSuggestionsView(APIView):
    def post(self, request):
        patient_context = request.data
        try:
            result = suggest_ccih_recommendations(patient_context)
            return Response({"result": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
