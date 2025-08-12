import itertools
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from vdf_monitor.models import VDF, Lectura
from pylogix import PLC

CHUNK_SIZE = 20  # cantidad de tags por lectura en lote

class Command(BaseCommand):
    help = 'Escanea todos los VDFs configurados (por PLC) y guarda sus lecturas en batch'

    def handle(self, *args, **options):
        now = timezone.now()

        # 1) Trae todos los VDF y arma índices
        vdfs = list(
            VDF.objects.all().values('id', 'ip', 'slot', 'tag')
        )
        if not vdfs:
            self.stdout.write("No hay VDFs configurados.")
            return

        # Índice para resolver rápido (ip,slot,tag) -> id
        vdf_index = {(v['ip'], v['slot'], v['tag']): v['id'] for v in vdfs}

        # Ordenar para agrupar por PLC
        vdfs_sorted = sorted(vdfs, key=lambda x: (x['ip'], x['slot']))

        # 2) Recorre por (ip, slot)
        for (ip, slot), group_iter in itertools.groupby(vdfs_sorted, key=lambda x: (x['ip'], x['slot'])):
            group = list(group_iter)
            tags = [g['tag'] for g in group]

            self.stdout.write(f"\n🔌 Conectando a {ip} (slot {slot}) para leer {len(tags)} tags…")

            # 2.1 Abrir conexión
            try:
                with PLC() as comm:
                    comm.IPAddress = ip
                    try:
                        # algunos PLC usan slot 0, otros 1/2; usa el de tu DB
                        comm.ProcessorSlot = int(slot) if slot is not None else 0
                    except Exception:
                        # por si slot viene None/str raro
                        comm.ProcessorSlot = 0

                    # 3) Leer en chunks
                    results_all = []
                    for i in range(0, len(tags), CHUNK_SIZE):
                        chunk = tags[i:i + CHUNK_SIZE]
                        try:
                            res = comm.Read(chunk)
                        except Exception as e:
                            self.stderr.write(f"❌ Error leyendo chunk {i//CHUNK_SIZE} en {ip}: {e}")
                            # placeholder con error
                            res = [
                                type('Resp', (), {'TagName': t, 'Value': None, 'Status': 'Error'})()
                                for t in chunk
                            ]
                        # normalizar a lista (pylogix devuelve obj o lista)
                        if not isinstance(res, list):
                            res = [res]
                        results_all.extend(res)

            except Exception as e:
                self.stderr.write(f"❌ No fue posible conectar a {ip}: {e}")
                # Marca todo como error
                results_all = [
                    type('Resp', (), {'TagName': t, 'Value': None, 'Status': 'CommError'})()
                    for t in tags
                ]

            # 4) Preparar lecturas con fecha válida SIEMPRE
            lecturas = []
            # Resolución de VDF una vez: evita .get() dentro del loop
            for r in results_all:
                tag_name = getattr(r, 'TagName', None)
                status = getattr(r, 'Status', '')
                value = getattr(r, 'Value', None) if status == 'Success' else None

                vdf_id = vdf_index.get((ip, slot, tag_name))
                if not vdf_id:
                    # tag inesperado, lo aviso y sigo
                    self.stderr.write(f"⚠ Tag '{tag_name}' no coincide con ningún VDF ({ip}, slot {slot}).")
                    continue

                # IMPORTANTE: setear fecha aquí si usas bulk_create
                lecturas.append(Lectura(
                    vdf_id=vdf_id,
                    valor=value,
                    timestamp=now,  # <-- fecha válida para evitar errores en admin/date_hierarchy
                    estado=status if status else None  # si tienes este campo
                ))
                self.stdout.write(f"   📦 {tag_name} → {value} ({status})")

            # 5) Insertar en lote con transacción
            if lecturas:
                with transaction.atomic():
                    Lectura.objects.bulk_create(lecturas, batch_size=500)
                self.stdout.write(f"✅ Guardadas {len(lecturas)} lecturas para {ip}")
            else:
                self.stdout.write("⚠ No se generaron lecturas para este PLC.")
