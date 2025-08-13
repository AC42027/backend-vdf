# vdf_monitor/admin.py
# ——————————————————————————————————————————————————————————————
# Admin de Django para gestionar VDF (variadores) y sus Lecturas.
# ——————————————————————————————————————————————————————————————

from django.contrib import admin                 # Importa el admin de Django
from .models import Division, Area, Zona, VDF, Lectura  # Importa tus modelos

@admin.register(VDF)
class VDFAdmin(admin.ModelAdmin):
    # list_display: columnas que se ven en la tabla del admin
    list_display  = ('nombre', 'division', 'area', 'zone', 'ip', 'tag', 'tipo')
    # list_filter: filtros laterales (debe ser lista/tupla)
    list_filter   = ['tipo', 'division', 'area', 'zone']
    # search_fields: búsqueda por estos campos (lista/tupla)
    search_fields = ['nombre', 'ip', 'tag', 'division', 'area', 'zone']
    # ordering: orden por defecto
    ordering      = ('division', 'area', 'zone', 'tipo', 'tag')
    # list_per_page: paginación en el admin
    list_per_page = 50


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
