from django.views.generic import TemplateView

from kstore.helpers.mixins import JerarquiaMixin

class ProfileView(JerarquiaMixin, TemplateView):
    template_name = 'kstore/users/profile.html'
    jerarquia = ['Home', 'Profile']
