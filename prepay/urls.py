from django.conf.urls import patterns, include, url
from django.contrib import admin
from prepay import views, settings
from prepay import startup

admin.autodiscover()

startup.set_groups()
startup.create_default_users()
#startup.create_default_listing()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^$', views.browse_listings, name='browse_listings'),
    url(r'^about$', views.about, name='about'),
    url(r'^category/(?P<category_id>.*)$', views.browse_category, name='browse_category'),
    url(r'^browse_listings/.*filter/(?P<fil>.*)$', views.browse_listings, name='filter'),
    #url(r'^browse_listings/search/$', views.browse_listings, name='search'),
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
    
    url(r'^addtocart/(?P<listing_id>.*)$', views.addtocart, name='addtocart'),
    url(r'^removefromcart/(?P<listing_id>.*)$', views.removefromcart, name='removefromcart'),
    url(r'^viewcart$', views.viewcart, name='viewcart'),
    
    url(r'^confirmed$', views.confirmed, name='confirmed'),
    url(r'^withdraw/(?P<order_id>.*)$', views.withdraw, name='withdraw'),
    url(r'^confirmreceipt/(?P<order_id>.*)$', views.confirmreceipt, name='confirmreceipt'),
    url(r'^review/(?P<order_id>.*)$', views.review, name='review'),
    url(r'^returns/(?P<order_id>.*)$', views.returns, name='returns'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^logout_successful/$', views.logout, name='auth_logout_next'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': "/logout_successful"}, name="auth_logout"),
    #url(r'^logout/$', 'django.contrib.auth.views.logout', views.index, name="auth_logout"),


    url(r'^confirmation_code_sent/(?P<user_username>.*)$', views.confirmation_code_sent, name='confirmation_code_sent'),
    url(r'^confirm_registration/(?P<confirmation_code>.*)/(?P<user_username>.*)$', views.confirm_registration, name='confirm_registration'),
    url(r'^invalid/confirm_registration/(?P<confirmation_code>.*)/(?P<user_username>.*)$', views.invalid_confirmation_code, name='invalid_confirmation'),
)




