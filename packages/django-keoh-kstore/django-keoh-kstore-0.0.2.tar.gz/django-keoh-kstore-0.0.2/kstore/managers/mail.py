#encoding:utf-8
from django.db import models

class MessageManager(models.Manager):

    def inbox(self, user):
        return self.filter(
            sended = True,
            recipient = user.pk
        ).order_by('-sended_at')
    def new_messages(self, user):
        return self.inbox(user).filter(readed=False)

    def sent(self, user):
        return self.filter(
            sended = True,
            sender = user.pk
        ).order_by('-created_at')

    def draft(self, user):
        return self.filter(
            sended = False,
            sender = user.pk
        ).order_by('-created_at')

    def important(self, user):
        return self.inbox(user).filter(important=True)
