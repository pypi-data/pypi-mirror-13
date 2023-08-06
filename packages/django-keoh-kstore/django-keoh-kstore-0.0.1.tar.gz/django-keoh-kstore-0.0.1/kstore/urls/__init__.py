from django.conf.urls import include, url

from kstore.views import ManageIndexView

urlpatterns = [
    url(r'^$', ManageIndexView.as_view(), name='index'),
    url(r'^users/', include('kstore.urls.users', namespace='users')),
    url(r'^products/', include('kstore.urls.products', namespace='products')),
    url(r'^mail/', include('kstore.urls.kmail', namespace='mail')),
]
