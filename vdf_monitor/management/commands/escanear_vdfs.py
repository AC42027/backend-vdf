# vdf_monitor/management/commands/escanear_vdfs.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from collections import defaultdict

from vdf_monitor.models import Vdf, Signal, Lectura

# ----------------------------------------
# Lector de tags con PyLogix (fallback a dummy)
# ----------------------------------------
def read_many(ip: str, slot: int, tags: list[str]) -> list[tuple[float | None, str]]:
    """
    Lee una lista de tags contra (ip, slot).
    Devuelve lista de pares (valor, estado) en el mismo orden de 'tags'.
    """
    try:
        from pylogix import PLC
    except Exception:
        # Fallback: no hay pylogix disponible
        out = []
        now_s = timezone.now().second
        for _ in tags:
            out.append((None, "NoDriver"))
        return out

    results = []
    try:
        with PLC() as comm:
            comm.IPAddress = ip
            comm.ProcessorSlot = slot
            # pylogix soporta listas
            rlist = comm.Read(tags)
            # A veces Read(tags) devuelve 1 objeto cuando len(tags)==1
            if not isinstance(rlist, list):
                rlist = [rlist]
            for r in rlist:
                try:
                    val = float(r.Value) if r.Value is not None else None
                except Exception:
                    val = None
                status = getattr(r, "Status", None) or "Success"
                results.append((val, status))
    except Exception as e:
        # Error de conexión: marca todos con falla
        fail = (None, f"ConnError:{type(e).__name__}")
        results = [fail] * len(tags)
    return results


class Command(BaseCommand):
    help = "Escanea todos los VDF leyendo sus Signals (tags) y guarda lecturas."

    def handle(self, *args, **options):
        # Prefetch para evitar N+1
        vdfs = (
            Vdf.objects
            .prefetch_related("signals")
            .order_by("zona__area__division__nombre", "zona__area__nombre", "zona__nombre", "nombre")
        )

        # Agrupa signals por (ip, slot) para leer en batch
        groups: dict[tuple[str, int], list[Signal]] = defaultdict(list)
        total_signals = 0
        for v in vdfs:
            sigs = list(v.signals.all())
            if not sigs:
                continue
            key = (v.ip, v.slot)
            groups[key].extend(sigs)
            total_signals += len(sigs)

        if not total_signals:
            self.stdout.write(self.style.WARNING("No hay Signals configuradas en ningún VDF."))
            return

        self.stdout.write(f"🔌 Escaneando {len(groups)} conexiones | {total_signals} tags…")

        now = timezone.now()
        nuevos = []

        # Recorre cada conexión y lee todos sus tags
        for (ip, slot), sigs in groups.items():
            tags = [s.tag for s in sigs]
            self.stdout.write(f" → {ip} (slot {slot}) | {len(tags)} tags…")
            resultados = read_many(ip, slot, tags)  # lista de (valor, estado)

            # Empareja resultado ↔ signal
            for sig, (valor, estado) in zip(sigs, resultados):
                nuevos.append(
                    Lectura(
                        signal=sig,
                        valor=valor,
                        timestamp=now,
                        estado=estado,
                    )
                )

        # Inserta en bloque
        if nuevos:
            with transaction.atomic():
                Lectura.objects.bulk_create(nuevos, batch_size=1000)
            self.stdout.write(self.style.SUCCESS(f"✅ Insertadas {len(nuevos)} lecturas."))
        else:
            self.stdout.write(self.style.WARNING("No se generaron lecturas."))
