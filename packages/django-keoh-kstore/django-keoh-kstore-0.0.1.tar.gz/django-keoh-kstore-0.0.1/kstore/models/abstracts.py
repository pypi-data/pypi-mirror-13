
from django.db import models

class BaseCompanyModel(models.Model):
    name = models.CharField('Name',max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True
