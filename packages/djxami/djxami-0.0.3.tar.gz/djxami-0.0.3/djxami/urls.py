from django.conf.urls import url, patterns
from djxami import views

urlpatterns = patterns('',
                       url('^$', views.Messages.as_view(), name="messages"),
                       url('^close/$', views.Close.as_view(), name="close"),
                       url('^stream/$', views.Stream.as_view(), name="stream"),
                       )
