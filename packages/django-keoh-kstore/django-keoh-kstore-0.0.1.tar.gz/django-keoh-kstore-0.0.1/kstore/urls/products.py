from django.conf.urls import include, url

from kstore.views import ProductView

urlpatterns = [
    url(r'^catalogo/$', ProductView.as_view(), name='catalogo'),
]
