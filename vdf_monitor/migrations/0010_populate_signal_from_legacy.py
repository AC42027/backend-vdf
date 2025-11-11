# vdf_monitor/migrations/000X_populate_signal_from_legacy.py
from django.db import migrations

def forwards(apps, schema_editor):
    Vdf     = apps.get_model('vdf_monitor', 'Vdf')
    Signal  = apps.get_model('vdf_monitor', 'Signal')
    Lectura = apps.get_model('vdf_monitor', 'Lectura')

    def map_metric(vdf):
        t = (getattr(vdf, 'tipo', '') or '').lower()
        if t.startswith('amp'):  return 'amp'
        if t.startswith('temp'): return 'temp'
        return 'amp'  # por defecto, si no tenemos tipo

    # Recorre lecturas sin signal pero con vdf legado
    qs = Lectura.objects.filter(signal__isnull=True).exclude(vdf__isnull=True)
    for lec in qs.iterator(chunk_size=1000):
        v = lec.vdf
        metric = map_metric(v)
        tag = getattr(v, 'tag', '') or f"VDF{v.id}_{metric}"

        # Crea/obtiene la señal correspondiente
        sig, _ = Signal.objects.get_or_create(
            vdf_id=v.id,
            metric=metric,
            defaults={'tag': tag}
        )

        # Asigna la signal a la lectura
        lec.signal_id = sig.id
        lec.save(update_fields=['signal'])

def backwards(apps, schema_editor):
    # No implementamos reversa (opcional)
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('vdf_monitor', '0009_alter_lectura_estado_alter_lectura_vdf_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
