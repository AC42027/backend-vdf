# vdf_monitor/models.py
from django.db import models  # Importa el ORM de Django
from django.utils import timezone
class VDF(models.Model):
    # Nombre físico del equipo (puede ir en blanco si aún no lo conoces)
    nombre = models.CharField("Nombre", max_length=100, blank=True)
    # IP del PLC/gateway desde donde se leen los tags asociados a este VDF
    ip = models.GenericIPAddressField()
    # Slot del CPU (siempre 0 para pylogix; lo dejamos por compatibilidad)
    slot = models.PositiveSmallIntegerField(default=0)
    # Nombre EXACTO del tag en el PLC (por ejemplo: VDF_CC01_Corrientes[0])
    tag = models.CharField(max_length=150)
    # Tipo de la señal para clasificar (corriente/temperatura)
    tipo = models.CharField(
        max_length=10,
        choices=[('Amp', 'Corriente'), ('Temp', 'Temperatura')]
    )
    # Campos para agrupar por ubicación/jerarquía (opcionales)
    division = models.CharField("División", max_length=50, blank=True)
    area     = models.CharField("Área",      max_length=50, blank=True)
    zone     = models.CharField("Zona",      max_length=50, blank=True)
    # Texto libre para detalles (gabinete, piso, etc.)
    descripcion = models.TextField("Descripción", blank=True)

    def __str__(self):
        # Cadena amigable para admin/listados
        mostrado = self.nombre if self.nombre else self.tag
        return f"{mostrado} | {self.ip}"

class Lectura(models.Model):
    # Relación con el VDF al que corresponde esta lectura
    vdf = models.ForeignKey(VDF, on_delete=models.CASCADE)
    # Valor leído (float). Puede ser nulo si la lectura falló
    valor = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    estado = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        # Muestra el tag y la hora de la lectura
        return f"{self.vdf} @ {self.timestamp}: {self.valor}"
