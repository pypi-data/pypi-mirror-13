#encoding:utf-8
from django.views.generic import ListView, View
from django.views.generic.detail import DetailView
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.text import slugify

from braces.views import LoginRequiredMixin

import datetime
import random

from kstore.helpers.mixins import JerarquiaMixin
from kstore.models import MailMessage
from kstore.forms import ComposeMailForm



class MailView(LoginRequiredMixin, JerarquiaMixin, ListView):
    template_name = 'kstore/mail/inbox.html'
    jerarquia = [_('Mail'), _('Inbox')]
    model = MailMessage
    context_object_name = 'messages'


    def get_context_data(self, **kwargs):
        context = super(MailView, self).get_context_data(**kwargs)
        message_list = MailMessage.objects.inbox(self.request.user)
        paginator = Paginator(message_list, 10)
        page = self.request.GET.get('page')
        try:
            context['messages'] = paginator.page(page)
        except PageNotAnInteger:
            context['messages'] = paginator.page(1)
        except EmptyPage:
            context['messages'] = paginator.page(paginator.num_pages)
        #context['messages'] = MailMessage.objects.inbox(self.request.user)
        context['new_messages'] = MailMessage.objects.new_messages(self.request.user).count()
        context['num_drafts'] = MailMessage.objects.draft(self.request.user).count()
        return context

class SentMailView(LoginRequiredMixin, JerarquiaMixin, ListView):
    template_name = 'kstore/mail/sent.html'
    jerarquia = [_('Mail'), _('Sent')]
    model = MailMessage
    context_object_name = 'messages'

    def get_context_data(self, **kwargs):
        context = super(SentMailView, self).get_context_data(**kwargs)
        message_list = MailMessage.objects.sent(self.request.user)
        paginator = Paginator(message_list, 10)
        page = self.request.GET.get('page')
        try:
            context['messages'] = paginator.page(page)
        except PageNotAnInteger:
            context['messages'] = paginator.page(1)
        except EmptyPage:
            context['messages'] = paginator.page(paginator.num_pages)
        #context['messages'] = MailMessage.objects.sent(self.request.user)
        context['new_messages'] = MailMessage.objects.new_messages(self.request.user).count()
        context['num_drafts'] = MailMessage.objects.draft(self.request.user).count()
        return context

class DraftMailView(LoginRequiredMixin, JerarquiaMixin, ListView):
    template_name = 'kstore/mail/draft.html'
    jerarquia = [_('Mail'), _('Draft')]
    model = MailMessage
    context_object_name = 'messages'

    def get_context_data(self, **kwargs):
        context = super(DraftMailView, self).get_context_data(**kwargs)
        message_list = MailMessage.objects.draft(self.request.user)
        paginator = Paginator(message_list, 10)
        page = self.request.GET.get('page')
        try:
            context['messages'] = paginator.page(page)
        except PageNotAnInteger:
            context['messages'] = paginator.page(1)
        except EmptyPage:
            context['messages'] = paginator.page(paginator.num_pages)
        #context['messages'] = MailMessage.objects.draft(self.request.user)
        context['new_messages'] = MailMessage.objects.new_messages(self.request.user).count()
        context['num_drafts'] = MailMessage.objects.draft(self.request.user).count()
        return context

class ImportantMailView(LoginRequiredMixin, JerarquiaMixin, ListView):
    template_name = 'kstore/mail/important.html'
    jerarquia = [_('Mail'), _('Favorite inbox')]
    model = MailMessage
    context_object_name = 'messages'


    def get_context_data(self, **kwargs):
        context = super(ImportantMailView, self).get_context_data(**kwargs)
        message_list = MailMessage.objects.important(self.request.user)
        paginator = Paginator(message_list, 10)
        page = self.request.GET.get('page')
        try:
            context['messages'] = paginator.page(page)
        except PageNotAnInteger:
            context['messages'] = paginator.page(1)
        except EmptyPage:
            context['messages'] = paginator.page(paginator.num_pages)
        #context['messages'] = MailMessage.objects.inbox(self.request.user)
        context['new_messages'] = MailMessage.objects.new_messages(self.request.user).count()
        context['num_drafts'] = MailMessage.objects.draft(self.request.user).count()
        return context

class MessageMailView(LoginRequiredMixin, JerarquiaMixin, View):
    template_name = 'kstore/mail/mailmessage_detail.html'
    jerarquia = [_('Mail'), _('Message')]

    def get(self, request, slug):
        message = MailMessage.objects.get(slug=slug)
        if message.recipient != request.user:
            return redirect('kstore:mail:inbox')
        message.readed=True
        message.save()
        return render(request, self.template_name, {'message': message})

class ComposeMailView(LoginRequiredMixin, JerarquiaMixin, View):
    """
        Vista donde escribiremos los emails. La CBV con metodo GET solo
        entrega el formulario vacio. Con metodo POST crea el mensaje en
        la base de datos directamente. Hay que cambiarlo para que sea
        el formulario através de su metodo save() el que grabe.
    """
    template_name = 'kstore/mail/compose_mail.html'
    form_class = ComposeMailForm

    def get(self, request):
        form = ComposeMailForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = ComposeMailForm(request.POST)
        if form.is_valid():
            for dest in form.cleaned_data["destinatario"]:
                msg = MailMessage(
                    subject=form.cleaned_data["subject"],
                    recipient=dest,
                    sender=request.user,
                    slug=slugify(form.cleaned_data["subject"]+str(random.randint(0,1000))),
                    sended_at=datetime.datetime.now(),
                    message=form.cleaned_data["message"],
                    sended=True
                )
                msg.save()

            return redirect('kstore:mail:inbox')
        else:
            return render(request, self.template_name, {'form':form})
