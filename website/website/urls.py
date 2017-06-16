# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.contrib.staticfiles import views


urlpatterns = [ 
    url(r'^admin/', admin.site.urls),
    
    url(r'^login/', login, name='login', kwargs={'template_name': 'authentication/pages/_login.html'}),
    url(r'^logout/$', logout, name='logout', kwargs={'next_page': '/'}),

    url(r'^', include('website.apps.phone.urls', namespace='phone')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]