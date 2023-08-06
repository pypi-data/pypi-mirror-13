#encoding:utf-8
from django.core.management.base import BaseCommand, CommandError

from kstore.models import BasicConfiguration

class Command(BaseCommand):
    '''
        Establece la configuracion inicial, que despues debera
        ser cambiada para adaptar a la empresa.
    '''
    def handle(self, *args, **options):

        try:
            config = BasicConfiguration.objects.all().first()
            self.stdout.write("Ya existe configuracion basica como "+config.company_name)
        except Exception as e:
            self.stdout.write("Estableciendo configuracion inicial.")
            bc = BasicConfiguration(company_name="Company Name")
            bc.save()
