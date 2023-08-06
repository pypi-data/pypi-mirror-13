from django.conf.urls import url, patterns
from djnotty import views

urlpatterns = patterns('',
                       url('^$', views.Messages.as_view(), name="messages"),
                       url('^close/$', views.Close.as_view(), name="close"),
                       )
