# vdf_monitor/views.py
from rest_framework import generics   # Vistas genéricas de DRF
from django.db.models import Q  # Filtros avanzados
from .models import Division, Area, Zona, VDF, Lectura
from .serializers import (
    DivisionSerializer,
    AreaSerializer,
    ZonaSerializer,
    VDFSerializer,
    LecturaSerializer,
)

class VDFListAPIView(generics.ListAPIView):
    """
    Lista todos los VDF con su última lectura.
    Permite filtrar por tipo/división/área/zona e incluso por IP/tag.
    También permite ordenar por nombre, tipo, tag, ip.
    """
    serializer_class = VDFSerializer

    def get_queryset(self):
        # Base: todos los VDF
        qs = VDF.objects.all()

        # --- Filtros por query params (sin depender de django-filter) ---
        tipo = self.request.query_params.get('tipo')          # 'Amp' | 'Temp'
        division = self.request.query_params.get('division')  # p.ej. 'Planta 1'
        area = self.request.query_params.get('area')          # p.ej. 'Línea A'
        zone = self.request.query_params.get('zone')          # p.ej. 'CC01'
        ip = self.request.query_params.get('ip')
        tag = self.request.query_params.get('tag')

        if tipo:
            qs = qs.filter(tipo=tipo)
        if division:
            qs = qs.filter(
                Q(zona__area__division__nombre=division) | Q(division=division)
            )
        if area:
            qs = qs.filter(Q(zona__area__nombre=area) | Q(area=area))
        if zone:
            qs = qs.filter(Q(zona__nombre=zone) | Q(zone=zone))
        if ip:
            qs = qs.filter(ip=ip)
        if tag:
            qs = qs.filter(tag=tag)

        # --- Ordenamiento simple por query param 'ordering' ---
        # Ej: ?ordering=nombre  | ?ordering=-tipo  | ?ordering=ip
        ordering = self.request.query_params.get('ordering')
        if ordering in {'nombre', '-nombre', 'tipo', '-tipo', 'tag', '-tag', 'ip', '-ip'}:
            qs = qs.order_by(ordering)
        else:
            # Orden por defecto (coherente: por división/área/zona y luego por tipo/tag)
            qs = qs.order_by('division', 'area', 'zone', 'tipo', 'tag')

        # --- Optimización opcional: prefetch de lecturas si quisieras histórico ---
        # (No es estrictamente necesario para 'latest', que ya se resuelve en el serializer)
        return qs


class DivisionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Division.objects.all().order_by("nombre")
    serializer_class = DivisionSerializer


class AreaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AreaSerializer

    def get_queryset(self):
        qs = Area.objects.select_related("division").order_by("division__nombre", "nombre")
        division_id = self.request.query_params.get("division_id")
        if division_id:
            qs = qs.filter(division_id=division_id)
        return qs


class ZonaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ZonaSerializer

    def get_queryset(self):
        qs = Zona.objects.select_related("area", "area__division").order_by(
            "area__division__nombre", "area__nombre", "nombre"
        )
        area_id = self.request.query_params.get("area_id")
        if area_id:
            qs = qs.filter(area_id=area_id)
        return qs

class LecturaListAPIView(generics.ListAPIView):
    """
    Lista lecturas (histórico). Acepta filtros por VDF y rango de fechas.
    Uso típico desde frontend:
      /api/lecturas/?vdf_id=12
      /api/lecturas/?vdf_id=12&desde=2025-08-05T00:00:00&hasta=2025-08-05T23:59:59
    """
    serializer_class = LecturaSerializer

    def get_queryset(self):
        qs = Lectura.objects.select_related('vdf').order_by('-timestamp')

        # Filtrar por vdf_id (numérico)
        vdf_id = self.request.query_params.get('vdf_id')
        if vdf_id:
            qs = qs.filter(vdf_id=vdf_id)

        # Filtro por rango de fechas (ISO 8601)
        desde = self.request.query_params.get('desde')  # ej: 2025-08-05T00:00:00
        hasta = self.request.query_params.get('hasta')  # ej: 2025-08-05T23:59:59
        if desde:
            qs = qs.filter(timestamp__gte=desde)
        if hasta:
            qs = qs.filter(timestamp__lte=hasta)

        return qs
