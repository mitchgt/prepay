from django.conf.urls import patterns, include, url
from django.contrib import admin
from prepay import views, settings

admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^$', views.index, name='index'),
    url(r'^$', views.browse, name='index'),
    url(r'^about$', views.about, name='about'),
    url(r'^browse_category/(?P<category_id>.*)$', views.browse_category, name='browse_category'),
    url(r'^browse$', views.browse, name='browse'),
    url(r'^register$', views.register, name = 'register'), ###Jennifer
    url(r'^listings/(?P<listing_id>.*)$', views.listing_detail, name='listing_detail'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

)
