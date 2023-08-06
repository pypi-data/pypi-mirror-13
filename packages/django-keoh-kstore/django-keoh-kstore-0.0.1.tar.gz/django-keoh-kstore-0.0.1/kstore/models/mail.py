from django.db import models
from django.conf import settings

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class MessageManager(models.Manager):

    def inbox(self, user):
        return self.filter(
            sended = True
        ).filter(
            recipient = user.pk
        )
    def new_messages(self, user):
        return self.inbox(user).filter(readed=False)

class MailMessage(models.Model):

    subject = models.CharField(u'Asunto', max_length=255)
    readed = models.BooleanField(default=False)
    sended = models.BooleanField(default=False)
    # sended_at = models.DateTimeField(auto_add_now=True)
    message = models.TextField(blank=True)
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
