#from django.conf.urls.defaults import patterns, include, url
from django.conf.urls import *

urlpatterns = patterns('',
    url(r'^$', 'lb2Cadencia.reuniao.views.home'),
    url(r'^cadencia/', 'lb2Cadencia.reuniao.views.cadencia'),
    url(r'^projeto/', 'lb2Cadencia.reuniao.views.projeto'),
    url(r'^base/', 'lb2Cadencia.reuniao.views.base'),
    url(r'^novacadencia/', 'lb2Cadencia.reuniao.views.novacadencia'),
)