# =============================================================================
# vdf_monitor/views.py
# =============================================================================
from rest_framework import generics
from django.db.models import Q

from .models import Division, Area, Zona, Vdf, Lectura
from .serializers import (
    DivisionSerializer,
    AreaSerializer,
    ZonaSerializer,
    VDFSerializer,
    LecturaSerializer,
)


# --------------------------- VDF list ---------------------------
class VDFListAPIView(generics.ListAPIView):
    """
    Lista VDFs. Permite filtrar por división/área/zona/ip y ordenar.
    (Los valores de amp/temp se obtienen desde /api/lecturas/.)
    """
    serializer_class = VDFSerializer

    def get_queryset(self):
        qs = Vdf.objects.all()

        # --- Filtros opcionales ---
        division = self.request.query_params.get('division')
        area     = self.request.query_params.get('area')
        zone     = self.request.query_params.get('zone')
        ip       = self.request.query_params.get('ip')

        if division:
            qs = qs.filter(Q(zona__area__division__nombre=division) | Q(division=division))
        if area:
            qs = qs.filter(Q(zona__area__nombre=area) | Q(area=area))
        if zone:
            qs = qs.filter(Q(zona__nombre=zone) | Q(zone=zone))
        if ip:
            qs = qs.filter(ip=ip)

        # --- Orden (sólo campos permitidos) ---
        ordering = self.request.query_params.get('ordering')
        if ordering in {
            'nombre','-nombre','ip','-ip',
            'zona__area__division__nombre','-zona__area__division__nombre',
            'zona__area__nombre','-zona__area__nombre',
            'zona__nombre','-zona__nombre',
        }:
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by(
                'zona__area__division__nombre',
                'zona__area__nombre',
                'zona__nombre',
                'nombre',
            )
        return qs


# ------------------------ División/Área/Zona ------------------------
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


# --------------------------- Lecturas (histórico / últimas) ---------------------------
class LecturaListAPIView(generics.ListAPIView):
    """
    Lista lecturas (histórico) con datos de la Signal y el VDF.
      /api/lecturas/?vdf_id=12
      /api/lecturas/?vdf_id=12&desde=YYYY-MM-DDTHH:MM:SS&hasta=YYYY-MM-DDTHH:MM:SS
      /api/lecturas/?ordering=-timestamp&limit=500&page_size=500 (DRF paginado)
    """
    serializer_class = LecturaSerializer

    def get_queryset(self):
        qs = (
            Lectura.objects
            .select_related('signal', 'signal__vdf')   # imprescindible para vdf_id/metric/tag
            .order_by('-timestamp')
        )

        vdf_id = self.request.query_params.get('vdf_id')
        if vdf_id:
            qs = qs.filter(signal__vdf_id=vdf_id)

        desde = self.request.query_params.get('desde')
        hasta = self.request.query_params.get('hasta')
        if desde:
            qs = qs.filter(timestamp__gte=desde)
        if hasta:
            qs = qs.filter(timestamp__lte=hasta)

        return qs
