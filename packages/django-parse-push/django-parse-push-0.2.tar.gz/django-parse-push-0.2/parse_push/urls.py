from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.DeviceTokenSetter.as_view(), name='parse-push.setter'),
)
