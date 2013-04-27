from django.conf.urls import patterns, include, url
from django.contrib import admin
from prepay import views, settings
from prepay import startup

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^$', views.browse_listings, name='index'),
    url(r'^about$', views.about, name='about'),
    url(r'^category/(?P<category_id>.*)$', views.browse_category, name='browse_category'),
    url(r'^browse_listings/.*filter/(?P<fil>.*)$', views.browse_listings, name='filter'),
    url(r'^browse_listings/search/$', views.browse_listings, name='search'),
    url(r'^browse_listings/$', views.browse_listings, name='browse_listings'),
    url(r'^browse_product_requests$', views.browse_product_requests, name='browse_product_requests'),
    url(r'^register$', views.register, name = 'register'), ###Jennifer
    url(r'^edit/(?P<user_username>.*)$', views.edit_profile, name = 'edit_profile'), 
    #url(r'^user/(?P<user_username>.*)$', views.profile, name = 'user'),  ####Jennifer new
    url(r'^profile/(?P<user_username>.*)$', views.profile, name = 'profile'), 
    url(r'^listings/(?P<listing_id>.*)$', views.listing_detail, name='listing_detail'),
    url(r'^orders/(?P<listing_id>.*)$', views.orders, name='orders'),
    url(r'^checkout/(?P<listing_id>.*)$', views.checkout, name='checkout'),
    url(r'^withdrawListing/(?P<listing_id>.*)$', views.withdrawListing, name='withdrawListing'),
    url(r'^confirmed$', views.confirmed, name='confirmed'),
    url(r'^withdraw/(?P<order_id>.*)$', views.withdraw, name='withdraw'),
    url(r'^confirmreceipt/(?P<order_id>.*)$', views.confirmreceipt, name='confirmreceipt'),
    url(r'^review/(?P<order_id>.*)$', views.review, name='review'),
    url(r'^returns/(?P<order_id>.*)$', views.returns, name='returns'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name="auth_logout"),
)

#startup.set_groups()
