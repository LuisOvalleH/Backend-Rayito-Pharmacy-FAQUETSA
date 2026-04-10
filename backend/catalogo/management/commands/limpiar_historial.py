from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from catalogo.models import Historial, ConfiguracionSistema

class Command(BaseCommand):
    help = 'Elimina registros viejos del historial de administradores'

    def handle(self, *args, **options):
        config = ConfiguracionSistema.objects.first()
        
        if not config or config.meses_retencion_historial == 0:
            self.stdout.write("Limpieza cancelada: Configurado como 'Nunca'")
            return

        dias = config.meses_retencion_historial * 30
        fecha_limite = timezone.now() - timedelta(days=dias)

        cantidad, _ = Historial.objects.filter(fecha__lt=fecha_limite).delete()

        self.stdout.write(self.style.SUCCESS(f'Se eliminaron {cantidad} registros antiguos.'))