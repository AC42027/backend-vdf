# vdf_monitor/models.py
# =============================================================================
# MODELOS DEL DOMINIO
# - Division / Area / Zona: jerarquía normalizada.
# - Vdf: equipo físico (variador).
# - Signal: “tag” perteneciente a un Vdf (pueden existir varias por métrica).
# - Lectura: valor en el tiempo de una Signal.
# =============================================================================

from django.db import models
from django.utils import timezone


# ========================= Jerarquía normalizada =========================
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


# ================================ Vdf ===================================
class Vdf(models.Model):
    """
    Equipo físico (variador). Un Vdf puede tener N señales: corriente, temperatura, etc.
    """
    nombre = models.CharField("Nombre", max_length=100, blank=True)
    ip = models.GenericIPAddressField()
    slot = models.PositiveSmallIntegerField(default=0)
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT, null=True, blank=True, related_name="vdfs")
    descripcion = models.TextField("Descripción", blank=True)

    # ---- Legado (removible cuando ya no se use) ----
    division = models.CharField("División (texto - legado)", max_length=50, blank=True)
    area     = models.CharField("Área (texto - legado)",      max_length=50, blank=True)
    zone     = models.CharField("Zona (texto - legado)",      max_length=50, blank=True)
    tag      = models.CharField("Tag (legado)", max_length=150, blank=True, default="")
    tipo     = models.CharField(
        "Tipo (legado)",
        max_length=10,
        choices=[('Amp', 'Corriente'), ('Temp', 'Temperatura')],
        blank=True,
        default="",
    )

    def __str__(self):
        mostrado = self.nombre if self.nombre else (self.tag or "VDF")
        return f"{mostrado} | {self.ip}"


# =============================== Signal =================================
class Signal(models.Model):
    """
    Señal/Tag que pertenece a un Vdf.
    - metric: tipo de métrica (amp/temp/...) → enum corto para filtrar.
    - tag: nombre/tag exacto del PLC/SCADA (único por VDF).
    """
    METRIC_CHOICES = [
        ('amp',  'Corriente (A)'),
        ('temp', 'Temperatura (°C)'),
    ]

    vdf    = models.ForeignKey(Vdf, on_delete=models.CASCADE, related_name="signals")
    metric = models.CharField(max_length=16, choices=METRIC_CHOICES, db_index=True)
    tag    = models.CharField(max_length=200)  # sin unique global

    class Meta:
        ordering = ["vdf_id", "metric", "tag"]
        constraints = [
            models.UniqueConstraint(fields=["vdf", "tag"], name="uq_signal_tag_por_vdf")
        ]

    def __str__(self):
        return f"{self.vdf} · {self.metric} · {self.tag}"


# =============================== Lectura ================================
class Lectura(models.Model):
    """
    Medición puntual en el tiempo de una Signal (histórico).
    """
    signal = models.ForeignKey(Signal, on_delete=models.CASCADE, related_name="lecturas")
    valor = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    estado = models.CharField(max_length=32, blank=True, default="")

    class Meta:
        indexes = [models.Index(fields=["signal", "-timestamp"])]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.signal} @ {self.timestamp:%Y-%m-%d %H:%M:%S}: {self.valor}"


# Alias temporal (si aún importas 'VDF' en mayúsculas desde otros módulos)
VDF = Vdf
