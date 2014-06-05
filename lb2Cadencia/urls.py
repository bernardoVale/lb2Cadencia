#from django.conf.urls.defaults import patterns, include, url
from django.conf.urls import *

urlpatterns = patterns('',
    url(r'^$', 'lb2Cadencia.reuniao.views.index'),
    url(r'^cadencia/', 'lb2Cadencia.reuniao.views.cadencia'),
)