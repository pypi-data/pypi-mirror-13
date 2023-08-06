#encoding:utf-8
from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify

from ckeditor.widgets import CKEditorWidget

def check_destinatarios(lista):
    for item in lista:
        if item[0] == '@':
            #print "destinatario: "+item
            continue
        else:
            #print "mal destinatario"
            continue

def limpia_destinatario(lista_destinatarios):
    lista1 = lista_destinatarios.split(",")
    check_destinatarios(lista1)
    lista = []
    for item in lista1:
        a,b = item.split("@")
        lista.append(b)
    return lista

class ComposeMailForm(forms.Form):

    subject = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class': 'MailWidget',
                'required': True
                }
            )
        )
    message = forms.CharField(
        widget=CKEditorWidget(
            config_name="mail_ckeditor"
            )
        )
    destinatario = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'Separados por comas',
                'class': 'MailWidget',
                'required': True
                }
            )
        )

    def clean_destinatario(self):
        self.dest = self.cleaned_data["destinatario"]
        self.dest = limpia_destinatario(self.dest)
        destinatarios = []
        for destinatario in self.dest:
            try:
                destinatario_provisional = User.objects.get(username=destinatario)
                destinatarios.append(destinatario_provisional)
            except User.DoesNotExist:
                raise forms.ValidationError("Destinatario incorrecto " + destinatario)
        return destinatarios
