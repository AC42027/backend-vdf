# =============================================================================
# vdf_monitor/admin.py
# Admin de Django para jerarquía, Vdf, Signal y Lectura.
# Incluye INLINE de Signal dentro de Vdf para editar múltiples tags por Vdf.
# =============================================================================

from django.contrib import admin
from .models import Division, Area, Zona, Vdf, Signal, Lectura


# --------------------------- Jerarquía ---------------------------
@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display  = ("id", "nombre")
    search_fields = ("nombre",)
    ordering      = ("nombre",)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display  = ("id", "division", "nombre")
    list_filter   = ("division",)
    search_fields = ("nombre", "division__nombre")
    ordering      = ("division__nombre", "nombre")


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display  = ("id", "area", "nombre")
    list_filter   = ("area__division", "area")
    search_fields = ("nombre", "area__nombre", "area__division__nombre")
    ordering      = ("area__division__nombre", "area__nombre", "nombre")


# ---------------------------- Signal inline ----------------------------
class SignalInline(admin.TabularInline):
    """
    Permite crear/editar señales (tags) dentro del formulario de Vdf.
    - Agrega tantas filas como necesites (amp, temp, etc.).
    """
    model = Signal
    fk_name = "vdf"
    fields = ("metric", "tag")
    extra = 2                # filas vacías por defecto
    can_delete = True        # permitir borrar señales
    verbose_name = "Señal (tag)"
    verbose_name_plural = "Señales (tags)"


# ----------------------------- Vdf admin -----------------------------
@admin.register(Vdf)
class VdfAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "ip", "slot", "division_name", "area_name", "zona_name")
    list_filter  = ("zona__area__division", "zona__area", "zona")
    search_fields = ("nombre", "ip", "descripcion",
                     "zona__nombre", "zona__area__nombre", "zona__area__division__nombre")
    ordering = ("zona__area__division__nombre", "zona__area__nombre", "zona__nombre", "nombre")
    fields   = ("nombre", "zona", "ip", "slot", "descripcion")
    autocomplete_fields = ("zona",)
    list_per_page = 50

    # Habilita edición de múltiples tags por Vdf
    inlines = [SignalInline]

    # Helpers para columnas legibles
    def division_name(self, obj): return obj.zona.area.division.nombre if obj.zona_id else obj.division or "—"
    division_name.short_description = "División"
    def area_name(self, obj): return obj.zona.area.nombre if obj.zona_id else obj.area or "—"
    area_name.short_description = "Área"
    def zona_name(self, obj): return obj.zona.nombre if obj.zona_id else obj.zone or "—"
    zona_name.short_description = "Zona"


# ---------------------------- Signal admin ----------------------------
@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display  = ("id", "vdf", "metric", "tag")
    list_filter   = ("metric", "vdf__zona__area__division")
    search_fields = ("tag", "vdf__nombre", "vdf__ip")
    autocomplete_fields = ("vdf",)
    ordering = ("vdf__zona__area__division__nombre", "vdf__zona__area__nombre",
                "vdf__zona__nombre", "vdf__nombre", "metric")


# ---------------------------- Lectura admin ----------------------------
@admin.register(Lectura)
class LecturaAdmin(admin.ModelAdmin):
    list_display = ("id", "signal", "vdf_nombre", "metric", "valor", "timestamp", "estado")
    list_filter  = ("signal__metric", "signal__vdf__zona__area__division",
                    "signal__vdf__zona__area", "signal__vdf__zona")
    search_fields = ("signal__tag", "signal__vdf__nombre")
    ordering = ("-timestamp",)
    date_hierarchy = "timestamp"
    autocomplete_fields = ("signal",)

    # Helpers para columnas
    def vdf_nombre(self, obj):
        return getattr(obj.signal.vdf, "nombre", None) or f"VDF #{obj.signal.vdf_id}"
    vdf_nombre.short_description = "VDF"

    def metric(self, obj):
        return getattr(obj.signal, "metric", "—")
    metric.short_description = "Métrica"
