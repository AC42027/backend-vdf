# Importa las utilidades de DRF para crear serializadores
from rest_framework import serializers
# Importa tus modelos VDF y Lectura
from .models import VDF, Lectura

class LecturaSerializer(serializers.ModelSerializer):
    """ Serializa una lectura individual (valor + fecha). """
    class Meta:
        model = Lectura                             # Modelo a serializar
        fields = ('valor', 'timestamp')             # Campos expuestos en la API

class VDFSerializer(serializers.ModelSerializer):
    """
    Serializa un VDF y adjunta su última lectura en el campo 'latest'.
    Esto evita tener que hacer otra llamada para ver el valor más reciente.
    """
    latest = serializers.SerializerMethodField()    # Campo calculado por método

    class Meta:
        model = VDF
        # Campos del VDF que exponemos en la API (incluye agrupaciones y descripción)
        fields = (
            'id', 'nombre', 'division', 'area', 'zone',
            'ip', 'slot', 'tag', 'tipo', 'descripcion',
            'latest',                                   # última lectura adjunta
        )

    def get_latest(self, obj):
        """
        Retorna la última lectura (por timestamp) del VDF.
        Soporta dos escenarios:
          1) Si el ForeignKey en Lectura usa related_name='lecturas', usamos obj.lecturas
          2) Si NO tiene related_name, usamos el manager por defecto: obj.lectura_set
        """
        # Intenta primero con 'lecturas' (caso limpio con related_name)
        rel = getattr(obj, 'lecturas', None)         # None si no existe el atributo

        # Si no hay 'lecturas', usa el manager inverso por defecto de Django
        if rel is None:
            rel = obj.lectura_set                    # ← nombre por defecto (SIN “s” extra)

        # Obtiene la última lectura por fecha (descendente); puede ser None si no hay datos
        ultimo = rel.order_by('-timestamp').first()

        # Si hay lectura, la serializamos; si no, devolvemos None
        return LecturaSerializer(ultimo).data if ultimo else None
