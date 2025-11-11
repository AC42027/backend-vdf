# vdf_monitor/serializers.py
# =============================================================================
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Division, Area, Zona, Vdf, Signal, Lectura


# --------------------------- Lecturas ---------------------------
class LecturaSerializer(serializers.ModelSerializer):
    vdf_id    = serializers.IntegerField(source="signal.vdf_id", read_only=True)
    signal_id = serializers.IntegerField(source="signal.id", read_only=True)
    metric    = serializers.CharField(source="signal.metric", read_only=True)
    tag       = serializers.CharField(source="signal.tag", read_only=True)

    class Meta:
        model  = Lectura
        fields = ("vdf_id", "signal_id", "metric", "tag", "valor", "timestamp", "estado")


# --------------------- Jerarquía normalizada ---------------------
class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Division
        fields = ("id", "nombre")


class AreaSerializer(serializers.ModelSerializer):
    division_nombre = serializers.CharField(source="division.nombre", read_only=True)

    class Meta:
        model  = Area
        fields = ("id", "division", "division_nombre", "nombre")


class ZonaSerializer(serializers.ModelSerializer):
    area_nombre     = serializers.CharField(source="area.nombre", read_only=True)
    division_nombre = serializers.CharField(source="area.division.nombre", read_only=True)

    class Meta:
        model  = Zona
        fields = ("id", "area", "area_nombre", "division_nombre", "nombre")


# ------------------------------ VDF ------------------------------
class VDFSerializer(serializers.ModelSerializer):
    zona = serializers.PrimaryKeyRelatedField(
        queryset=Zona.objects.all(), allow_null=True, required=False
    )
    division_name = serializers.SerializerMethodField()
    area_name     = serializers.SerializerMethodField()
    zona_name     = serializers.SerializerMethodField()

    class Meta:
        model  = Vdf
        fields = (
            "id",
            "nombre",
            "ip",
            "slot",
            "descripcion",
            "zona",
            "division_name",
            "area_name",
            "zona_name",
        )

    def get_division_name(self, obj):
        return obj.zona.area.division.nombre if getattr(obj, "zona_id", None) else getattr(obj, "division", None)

    def get_area_name(self, obj):
        return obj.zona.area.nombre if getattr(obj, "zona_id", None) else getattr(obj, "area", None)

    def get_zona_name(self, obj):
        return obj.zona.nombre if getattr(obj, "zona_id", None) else getattr(obj, "zone", None)


# ------------------------------ SIGNAL ------------------------------
class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = ("id", "vdf", "metric", "tag")
        validators = [
            UniqueTogetherValidator(
                queryset=Signal.objects.all(),
                fields=["vdf", "tag"],
                message="Este Tag ya existe en este VFD."
            )
        ]
