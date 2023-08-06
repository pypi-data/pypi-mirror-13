from django.conf.urls import include, url

from kstore.views import MailView

urlpatterns = [
    url(r'^$', MailView.as_view(), name='inbox'),
]
