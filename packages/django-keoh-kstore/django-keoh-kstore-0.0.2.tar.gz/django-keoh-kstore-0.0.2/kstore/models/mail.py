#encoding:utf-8
from django.db import models
from django.conf import settings

from ckeditor.fields import RichTextField
from uuidfield import UUIDField

from kstore.managers.mail import MessageManager

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class MailMessage(models.Model):

    subject = models.CharField(u'Asunto', max_length=255)
    slug = models.SlugField(unique=True)
    uuid = UUIDField(auto=True)
    readed = models.BooleanField(default=False)
    sended = models.BooleanField(default=False)
    sended_at = models.DateTimeField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    message = RichTextField(config_name='mail_ckeditor', blank=True)
    important = models.BooleanField(default=False)
    sender = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name='enviante'
    )
    recipient = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name='destinatario',
        null=True,
        blank=True
    )
    objects = MessageManager()

    def __unicode__(self):
        return self.subject

class MailContact(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name='Contacto'
    )

    owner = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name='registrador_de_contacto'
    )

    def full_name(self):
        fn = self.user.first_name + ' ' + self.user.last_name
        return fn

    def __unicode__(self):
        return self.full_name()
