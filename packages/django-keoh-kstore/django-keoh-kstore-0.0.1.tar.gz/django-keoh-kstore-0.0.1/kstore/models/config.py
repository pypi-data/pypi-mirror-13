from django.db import models

class BasicConfiguration(models.Model):
    company_name = models.CharField('Nombre de la empresa', max_length=255)

    def __unicode__(self):
        return self.company_name + ' configuration'
