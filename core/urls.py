from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.ingestion.urls')),
    path('qdrant/', include('apps.qdrant.urls')),
    path('api/sepsis/', include('apps.sepsis.urls')),
    path("api/protocols/", include("apps.protocols.urls")),
    path("api/agent/", include("apps.agent.urls")),
    path("api/health-check/", lambda r: JsonResponse({"status": "ok"})),
]
