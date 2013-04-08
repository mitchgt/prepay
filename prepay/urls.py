from django.conf.urls import patterns, include, url
from django.contrib import admin
from prepay import views, settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^$', views.browse_listings, name='index'),
    url(r'^about$', views.about, name='about'),
    url(r'^category/(?P<category_id>.*)$', views.browse_category, name='browse_category'),
    url(r'^browse_listings/search/$', views.browse_listings, name='search'),
    url(r'^browse_listings/$', views.browse_listings, name='browse_listings'),
#    url(r'^browse_product_requests$', views.browse_product_requests, name='browse_product_requests'),
    url(r'^register$', views.register, name = 'register'), ###Jennifer
    url(r'^edit/(?P<user_username>.*)$', views.edit_profile, name = 'edit_profile'), 
#    url(r'^user/(?P<user_username>.*)$', views.profile, name = 'user'),  ####Jennifer new
    url(r'^profile/(?P<user_username>.*)$', views.profile, name = 'profile'), 
    url(r'^listings/(?P<listing_id>.*)$', views.listing_detail, name='listing_detail'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
