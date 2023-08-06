from django.conf.urls import include, url

from kstore.views import ProfileView

urlpatterns = [
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
]
