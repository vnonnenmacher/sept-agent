# apps/sepsis/views.py

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import SepsisEpisodeDetailSerializer
from rest_framework.generics import ListAPIView
from .serializers import SepsisEpisodeListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from .models import SepsisEpisode


class SepsisEpisodeDetailView(RetrieveAPIView):
    queryset = SepsisEpisode.objects.select_related('patient')
    serializer_class = SepsisEpisodeDetailSerializer
    lookup_field = 'id'


class SepsisEpisodeListView(ListAPIView):
    queryset = SepsisEpisode.objects.select_related('patient')
    serializer_class = SepsisEpisodeListSerializer

    def get_queryset(self):
        queryset = self.queryset

        # 🔍 Filter by status
        status = self.request.query_params.get('status')
        if status == 'open':
            queryset = queryset.filter(ended_at__isnull=True)
        elif status == 'closed':
            queryset = queryset.filter(ended_at__isnull=False)

        # 🔍 Filter by patient name (case-insensitive contains)
        patient_name = self.request.query_params.get('patient_name')
        if patient_name:
            queryset = queryset.filter(patient__name__icontains=patient_name)

        # 🔍 Filter by start date range
        start_after = self.request.query_params.get('start_after')
        if start_after:
            queryset = queryset.filter(started_at__date__gte=start_after)

        start_before = self.request.query_params.get('start_before')
        if start_before:
            queryset = queryset.filter(started_at__date__lte=start_before)

        return queryset.order_by('-started_at')


class SepsisStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 🔥 Base queryset: Open episodes
        open_episodes = SepsisEpisode.objects.filter(ended_at__isnull=True)

        total_open = open_episodes.count()

        # 🔬 Open episodes without any culture requested
        open_without_culture = open_episodes.annotate(
            culture_count=Count('cultureresult')
        ).filter(culture_count=0).count()

        # 💉 Open episodes without any antibiotic administration
        open_without_antibiotic = open_episodes.annotate(
            antibiotic_count=Count('antibioticadministration')
        ).filter(antibiotic_count=0).count()

        # ⚠️ Open episodes with positive cultures
        open_with_positive_culture = open_episodes.filter(
            cultureresult__positive=True
        ).distinct().count()

        return Response({
            "total_open_episodes": total_open,
            "open_episodes_without_culture": open_without_culture,
            "open_episodes_without_antibiotic": open_without_antibiotic,
            "open_episodes_with_positive_culture": open_with_positive_culture,
        })
