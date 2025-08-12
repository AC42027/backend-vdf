import json
from django.core.management.base import BaseCommand
from vdf_monitor.models import VDF

class Command(BaseCommand):
    help = 'Carga VDFs desde devices.json'

    def handle(self, *args, **options):
        with open('devices.json') as f:
            devices = json.load(f)
        for dev in devices:
            ip   = dev['ip']
            slot = dev.get('slot', 0)
            for tag in dev['tags']:
                # inferir tipo por nombre
                tipo = 'Amp' if 'Amp' in tag else 'Temp'
                obj, created = VDF.objects.get_or_create(
                    ip=ip, slot=slot, tag=tag, defaults={'tipo': tipo}
                )
                if created:
                    self.stdout.write(f'+ Creado VDF: {ip} {tag}')
                else:
                    self.stdout.write(f'· Ya existe: {ip} {tag}')
