# vdf_monitor/migrations/00XX_make_signal_nonnull.py
# ============================================================================
# Objetivo de esta migración (manual):
#  1) Asegurar que NINGUNA fila quede con lecturas.signal = NULL
#     - para eso creamos/reusamos un Vdf/Signal "ORPHAN" y asignamos ahí
#       cualquier remanente que quede con NULL (defensa final).
#  2) Alterar la columna 'signal' de Lectura a NOT NULL (null=False) sin prompt.
# ----------------------------------------------------------------------------
# Nota:
#  Hacemos la limpieza con RunPython ANTES de AlterField. Así garantizamos que
#  el ALTER de NOT NULL no falle por datos faltantes.
# ============================================================================

from django.db import migrations, models

def ensure_no_null_signals(apps, schema_editor):
    """
    Paso de datos: garantizar que TODAS las lecturas tengan 'signal' asignado.
    Si queda alguna en NULL, se asigna a una señal 'ORPHAN_AMP' de un Vdf 'ORPHAN'.
    Este paso es idempotente: si no hay NULL, no hace nada.
    """
    # Obtenemos modelos "históricos" compatibles con el estado de esta migración
    Vdf     = apps.get_model('vdf_monitor', 'Vdf')
    Signal  = apps.get_model('vdf_monitor', 'Signal')
    Lectura = apps.get_model('vdf_monitor', 'Lectura')

    # ¿Quedan lecturas con signal=NULL?
    orphans_qs = Lectura.objects.filter(signal__isnull=True)
    if not orphans_qs.exists():
        return  # Nada que hacer

    # Creamos (o reusamos) un Vdf placeholder
    vdf_placeholder, _ = Vdf.objects.get_or_create(
        nombre="ORPHAN",
        ip="0.0.0.0",
        defaults={"slot": 0, "descripcion": "Placeholder para lecturas huérfanas"}
    )

    # Creamos (o reusamos) una Signal placeholder del tipo 'amp'
    sig_placeholder, _ = Signal.objects.get_or_create(
        vdf=vdf_placeholder,
        metric='amp',
        defaults={"tag": "ORPHAN_AMP"}
    )

    # Asignamos en bloque todas las lecturas que siguen sin señal
    orphans_qs.update(signal=sig_placeholder)


class Migration(migrations.Migration):

    # Django rellena dependencies automáticamente al crear la --empty;
    # si no lo hizo, añade aquí la última migración como dependencia.
    dependencies = [
        ('vdf_monitor', '0010_populate_signal_from_legacy'),  # <-- AJUSTA si fuese necesario
    ]

    operations = [
        # 1) Paso de datos: aseguramos no-NULL en 'signal'
        migrations.RunPython(ensure_no_null_signals, migrations.RunPython.noop),

        # 2) ALTER COLUMN: ponemos el FK 'signal' como NOT NULL (null=False)
        migrations.AlterField(
            model_name='lectura',
            name='signal',
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name='lecturas',
                to='vdf_monitor.signal',
                null=False,       # <--- clave: ya no permite NULL
                blank=False       # <--- coherente con el modelo
            ),
        ),
    ]
