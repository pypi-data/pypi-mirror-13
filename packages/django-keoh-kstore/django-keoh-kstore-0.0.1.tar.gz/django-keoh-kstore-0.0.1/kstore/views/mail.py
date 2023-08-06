from django.views.generic import ListView

from kstore.helpers.mixins import JerarquiaMixin

from kstore.models import MailMessage

class MailView(JerarquiaMixin, ListView):
    template_name = 'kstore/mail/inbox.html'
    jerarquia = ['Mail', 'Inbox']
    model = MailMessage
    context_object_name = 'messages'

    def get_context_data(self, **kwargs):
        context = super(MailView, self).get_context_data(**kwargs)
        context['messages'] = MailMessage.objects.inbox(self.request.user)
        context['new_messages'] = MailMessage.objects.new_messages(self.request.user).count()
        return context
