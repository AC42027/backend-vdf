# vdf_monitor/admin.py
# ——————————————————————————————————————————————————————————————
# Admin de Django para gestionar VDF (variadores) y sus Lecturas.
# ——————————————————————————————————————————————————————————————

from django.contrib import admin                 # Importa el admin de Django
from .models import Division, Area, Zona, VDF, Lectura  # Importa tus modelos


@admin.register(VDF)
class VDFAdmin(admin.ModelAdmin):
    """Formulario del admin para VDF.

    Se usa la relación normalizada ``zona`` para elegir ubicación y se excluyen
    los antiguos campos de texto ``division``, ``area`` y ``zone`` para evitar
    confusiones al crear/editar.
    """

    # Mostrar la jerarquía resuelta en la lista
    list_display = (
        "nombre",
        "division_name",
        "area_name",
        "zona_name",
        "ip",
        "tag",
        "tipo",
    )

    # Filtros y búsquedas sobre la jerarquía normalizada
    list_filter = ["tipo", "zona__area__division", "zona__area", "zona"]
    search_fields = [
        "nombre",
        "ip",
        "tag",
        "zona__nombre",
        "zona__area__nombre",
        "zona__area__division__nombre",
        "division",
        "area",
        "zone",
    ]

    ordering = (
        "zona__area__division__nombre",
        "zona__area__nombre",
        "zona__nombre",
        "tipo",
        "tag",
    )

    # Formulario solo con la zona normalizada y demás datos del VDF
    fields = ("nombre", "zona", "ip", "slot", "tag", "tipo", "descripcion")
    autocomplete_fields = ("zona",)

    list_per_page = 50

    # --------------------
    # Helpers para mostrar la jerarquía
    # --------------------
    def division_name(self, obj):
        return obj.zona.area.division.nombre if obj.zona_id else obj.division

    division_name.short_description = "División"

    def area_name(self, obj):
        return obj.zona.area.nombre if obj.zona_id else obj.area

    area_name.short_description = "Área"

    def zona_name(self, obj):
        return obj.zona.nombre if obj.zona_id else obj.zone

    zona_name.short_description = "Zona"


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("division", "nombre")
    list_filter = ("division",)
    search_fields = ("nombre", "division__nombre")
    ordering = ("division__nombre", "nombre")


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ("area", "nombre")
    list_filter = ("area__division", "area")
    search_fields = ("nombre", "area__nombre", "area__division__nombre")
    ordering = ("area__division__nombre", "area__nombre", "nombre")

@admin.register(Lectura)
class LecturaAdmin(admin.ModelAdmin):
    # Muestra el VDF asociado, valor y timestamp
    list_display   = ('id', 'vdf', 'valor', 'timestamp', 'estado')
    # Permite filtrar por tipo y nombre del VDF relacionado
    list_filter    = ['vdf__tipo', 'vdf__nombre']
    # Permite buscar por el tag del VDF
    search_fields  = ['vdf__tag']
    # Ordena de más reciente a más antiguo
    ordering       = ('-timestamp',)
    # Navegación por fecha en la parte superior
    date_hierarchy = 'timestamp'
