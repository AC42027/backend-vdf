# Importa las utilidades de DRF para crear serializadores
from rest_framework import serializers
# Importa tus modelos VDF y Lectura
from .models import Division, Area, Zona, VDF, Lectura

class LecturaSerializer(serializers.ModelSerializer):
    """ Serializa una lectura individual (valor + fecha). """
    class Meta:
        model = Lectura                             # Modelo a serializar
        fields = ('valor', 'timestamp')             # Campos expuestos en la API

class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ("id", "nombre")


class AreaSerializer(serializers.ModelSerializer):
    division_nombre = serializers.CharField(source="division.nombre", read_only=True)

    class Meta:
        model = Area
        fields = ("id", "division", "division_nombre", "nombre")


class ZonaSerializer(serializers.ModelSerializer):
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)
    division_nombre = serializers.CharField(source="area.division.nombre", read_only=True)

    class Meta:
        model = Zona
        fields = ("id", "area", "area_nombre", "division_nombre", "nombre")


class VDFSerializer(serializers.ModelSerializer):
    """Serializa un VDF y adjunta su última lectura en el campo 'latest'."""

    latest = serializers.SerializerMethodField()    # Campo calculado por método
    division = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    zona = serializers.PrimaryKeyRelatedField(
        queryset=Zona.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = VDF
        fields = (
            "id",
            "nombre",
            "division",
            "area",
            "zone",
            "zona",
            "ip",
            "slot",
            "tag",
            "tipo",
            "descripcion",
            "latest",
        )

    def get_division(self, obj):
        if obj.zona_id:
            return obj.zona.area.division.nombre
        return obj.division

    def get_area(self, obj):
        if obj.zona_id:
            return obj.zona.area.nombre
        return obj.area

    def get_zone(self, obj):
        if obj.zona_id:
            return obj.zona.nombre
        return obj.zone

    def get_latest(self, obj):
        """Retorna la última lectura (por timestamp) del VDF."""

        # Intenta primero con 'lecturas' (caso limpio con related_name)
        rel = getattr(obj, "lecturas", None)

        # Si no hay 'lecturas', usa el manager inverso por defecto de Django
        if rel is None:
            rel = obj.lectura_set

        # Obtiene la última lectura por fecha (descendente); puede ser None si no hay datos
        ultimo = rel.order_by("-timestamp").first()

        # Si hay lectura, la serializamos; si no, devolvemos None
        return LecturaSerializer(ultimo).data if ultimo else None
