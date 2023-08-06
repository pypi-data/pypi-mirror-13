from datetime import date

from django.shortcuts import render
from django.views.generic import TemplateView

from kstore.helpers.dates import get_week
from kstore.helpers.mixins import JerarquiaMixin, DateRangeMixin

class ManageIndexView(JerarquiaMixin, DateRangeMixin, TemplateView):
    template_name = 'kstore/dashboard/home.html'
    jerarquia = ['Home', 'Dashboard']
    dates = get_week(date.today())
