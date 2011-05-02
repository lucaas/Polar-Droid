from django.conf.urls.defaults import *
from views import upload, view, apply_filter, revert
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^upload/$', upload),
    (r'^view/(\d{1,3})/$', view),
    (r'^filter/(?P<photo_id>\d{1,3})/(?P<operation>\w+)/$', apply_filter),
    (r'^revert/(?P<photo_id>\d{1,3})/$', revert),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
