from django.conf.urls.defaults import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from django.contrib.auth.views import login, logout

urlpatterns = patterns('polardroid.photos.views',
    # Example:
	url(r'^login/$', login),
	url(r'^logout/$', logout),
	url(r'^$', 'index'),
	url(r'^profile/$', 'profile'),	
	url(r'^profile/(?P<user_id>\d+)/$', 'profile'),	
	url(r'^profile/(?P<user_id>\d+)/(?P<page>\d{1,3})/$', 'profile'),
	url(r'^edit_profile/$', 'edit_profile'),
	
	url(r'^browse/$', 'browse'),	
	url(r'^browse/(?P<filter>\w+)/$', 'browse'),	
	url(r'^browse/(?P<filter>\w+)/(?P<page>\d{1,3})/$', 'browse'),	
    url(r'^upload/$', 'upload'),
	
    url(r'^view/(\d{1,3})/$', 'view'),
	url(r'^edit/(\d{1,3})/$', 'edit'),
	url(r'^delete/(\d{1,3})/$', 'delete'),
	url(r'^view/(\d{1,3})/details/$', 'details'),
    url(r'^filter/(?P<photo_id>\d{1,3})/(?P<operation>\w+)/$', 'apply_filter'),
    url(r'^revert/(?P<photo_id>\d{1,3})/$', 'revert'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
