from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'mainapp.views.home', name='home'),
    url(r'^directorio/$', 'mainapp.views.allPages', name='directorio'),
    url(r'^directorio/nuevo/$', 'mainapp.views.nuevaWeb', name='nuevaWeb'),
    url(r'^tags_input/', include('tags_input.urls', namespace='tags_input')),
    
    url(r'^login/$', 'mainapp.views.appLogin'),
    url(r'^logout/$', 'mainapp.views.appLogout'),
    url(r'^registro/$', 'mainapp.views.appRegistro'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
