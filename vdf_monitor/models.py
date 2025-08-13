# vdf_monitor/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

# ---------------------------
# Jerarquía normalizada
# ---------------------------

class Division(models.Model):
    nombre = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Area(models.Model):
    division = models.ForeignKey(Division, on_delete=models.PROTECT, related_name="areas")
    nombre = models.CharField(max_length=80)

    class Meta:
        unique_together = ("division", "nombre")
        ordering = ["division__nombre", "nombre"]

    def __str__(self):
        return f"{self.division} / {self.nombre}"


class Zona(models.Model):
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="zonas")
    nombre = models.CharField(max_length=80)

    class Meta:
        unique_together = ("area", "nombre")
        ordering = ["area__division__nombre", "area__nombre", "nombre"]

    def __str__(self):
        return f"{self.area} / {self.nombre}"


# ---------------------------
# VDF y Lectura
# ---------------------------

class VDF(models.Model):
    # Nombre físico del equipo (puede ir en blanco)
    nombre = models.CharField("Nombre", max_length=100, blank=True)

    # IP del PLC/gateway desde donde se leen los tags asociados a este VDF
    ip = models.GenericIPAddressField()

    # Slot del CPU (pylogix usa 0, se deja por compatibilidad)
    slot = models.PositiveSmallIntegerField(default=0)

    # Nombre EXACTO del tag en el PLC (por ejemplo: VDF_CC01_Corrientes[0])
    tag = models.CharField(max_length=150)

    # Tipo de la señal para clasificar (corriente/temperatura)
    tipo = models.CharField(
        max_length=10,
        choices=[('Amp', 'Corriente'), ('Temp', 'Temperatura')]
    )

    # --- Campos de texto existentes (se mantienen para migrar / compatibilidad) ---
    division = models.CharField("División (texto)", max_length=50, blank=True)
    area     = models.CharField("Área (texto)",      max_length=50, blank=True)
    zone     = models.CharField("Zona (texto)",      max_length=50, blank=True)

    # --- NUEVO: relación normalizada (recomendada) ---
    # Asignando la zona podemos inferir área y división
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT, null=True, blank=True, related_name="vdfs")

    # Texto libre para detalles (gabinete, piso, etc.)
    descripcion = models.TextField("Descripción", blank=True)

    def clean(self):
        # Si en el futuro agregas validaciones adicionales, este es el lugar
        if self.zona is None and any([self.division, self.area, self.zone]):
            # No es error, solo aviso si quieres obligar a usar zona normalizada
            pass

    def __str__(self):
        mostrado = self.nombre if self.nombre else self.tag
        return f"{mostrado} | {self.ip}"

    # Helpers de sólo lectura para mostrar en admin/API
    @property
    def division_obj(self):
        return self.zona.area.division if self.zona_id else None

    @property
    def area_obj(self):
        return self.zona.area if self.zona_id else None

    @property
    def zona_obj(self):
        return self.zona if self.zona_id else None


class Lectura(models.Model):
    # IMPORTANTE: related_name='lecturas' para usar obj.lecturas en lugar de lectura_set
    vdf = models.ForeignKey(VDF, on_delete=models.CASCADE, related_name="lecturas", db_index=True)

    # Valor leído (float). Puede ser nulo si la lectura falló
    valor = models.FloatField(null=True, blank=True)

    # Índice para consultas por tiempo
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # Estado opcional
    estado = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.vdf} @ {self.timestamp:%Y-%m-%d %H:%M:%S}: {self.valor}"

