#~*~ coding: utf-8 ~*~
from django.conf.urls import *

from virtenviro.registration.views import signup


urlpatterns = patterns('',
    url( r'^signup/$', signup ),
    url( r'^login/$', 'django.contrib.auth.views.login', { "template_name": "virtenviro/accounts/login.html"} ),
    url( r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout' ),
)