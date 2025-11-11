# vdf_project/urls.py
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings

from vdf_monitor.views import (
    VDFListAPIView,
    LecturaListAPIView,
    DivisionListCreateAPIView,
    AreaListCreateAPIView,
    ZonaListCreateAPIView,
)

# Prefijo público que tienes en settings.FORCE_SCRIPT_NAME
PREFIX = (getattr(settings, "FORCE_SCRIPT_NAME", "") or "").lstrip("/")  # "vfd_monitoring/backend-vdf"

urlpatterns = [
    # ===================== CON PREFIJO (lo que esperas usar) =====================
    path(f"{PREFIX}/admin/", admin.site.urls),
    path(f"{PREFIX}/", RedirectView.as_view(url=f"/{PREFIX}/admin/", permanent=False)),

    path(f"{PREFIX}/api/divisiones/", DivisionListCreateAPIView.as_view(), name="division-list"),
    path(f"{PREFIX}/api/areas/",      AreaListCreateAPIView.as_view(),      name="area-list"),
    path(f"{PREFIX}/api/zonas/",      ZonaListCreateAPIView.as_view(),      name="zona-list"),
    path(f"{PREFIX}/api/vdfs/",       VDFListAPIView.as_view(),             name="vdf-list"),
    path(f"{PREFIX}/api/lecturas/",   LecturaListAPIView.as_view(),         name="lectura-list"),

    # ================== SIN PREFIJO (fallback defensivo) ==================
    # Si el servidor te “recorta” el prefijo (root_path/SCRIPT_NAME),
    # estas rutas permiten que /admin/ y /api/... sigan funcionando.
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/admin/", permanent=False)),

    path("api/divisiones/", DivisionListCreateAPIView.as_view(), name="division-list-np"),
    path("api/areas/",      AreaListCreateAPIView.as_view(),      name="area-list-np"),
    path("api/zonas/",      ZonaListCreateAPIView.as_view(),      name="zona-list-np"),
    path("api/vdfs/",       VDFListAPIView.as_view(),             name="vdf-list-np"),
    path("api/lecturas/",   LecturaListAPIView.as_view(),         name="lectura-list-np"),
]
