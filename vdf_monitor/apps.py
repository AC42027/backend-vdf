from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django.apps import AppConfig
import atexit

class VdfMonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vdf_monitor'

    def ready(self):
        scheduler = BackgroundScheduler()
        
        # Ejecutar cada 30 segundos
        scheduler.add_job(
            lambda: call_command('escanear_vdfs'),
            'interval',
            seconds=3600
        )

        scheduler.start()

        # Apagar el scheduler cuando se cierre Django
        atexit.register(lambda: scheduler.shutdown())
