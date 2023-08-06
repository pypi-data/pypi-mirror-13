# ~*~ coding: utf-8 ~*~
from django.conf.urls import url, include
from django.conf import settings
from django import __version__

if __version__.startswith('1.9'):
    app_name = 'vadmin'

    urlpatterns = [
        url(r'^$', 'virtenviro.admin.views.index', name='home'),
    ]

    if 'virtenviro.content' in settings.INSTALLED_APPS:
        urlpatterns += [
            url(r'^content/$', 'virtenviro.content.admin_views.content_page', name='content'),
            url(r'^content/(?P<page_id>\d+)/$', 'virtenviro.content.admin_views.content_page_edit',
                name='content_page_edit'),
            url(r'^content/add/$', 'virtenviro.content.admin_views.content_page_add', name='content_page_add'),
        ]

    if 'virtenviro.shop' in settings.INSTALLED_APPS:
        urlpatterns += [
            url(r'^shop/$', 'virtenviro.admin.views.shop', name='vadmin_shop'),
            url(r'^shop/import_yml/$', 'virtenviro.shop.views.import_yml', name='vadmin_import_yml'),
        ]
else:
    from django.conf.urls import patterns

    urlpatterns = patterns('',
                           url(r'^$', 'virtenviro.admin.views.index', name='home'), )

    if 'virtenviro.shop' in settings.INSTALLED_APPS:
        urlpatterns += patterns('',
                                url(r'^shop/$', 'virtenviro.admin.views.shop', name='vadmin_shop'),
                                url(r'^shop/import_yml/$', 'virtenviro.shop.views.import_yml',
                                    name='vadmin_import_yml'),
                                )
