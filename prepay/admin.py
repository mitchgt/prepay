from django.contrib import admin
from django.contrib.auth.models import User
from prepay.models import Product, Category, Seller, Listing, Bank, Escrow, BankAccount
from prepay.models import Buyer, ProductRequest, BankAccount, PhoneNumber, InstantMessenger
from prepay.models import StreetAddress, WebSite, Order, Cart
from django.contrib.contenttypes import generic

class PhoneNumberInline(generic.GenericTabularInline):
    model = PhoneNumber
    extra = 1

class InstantMessengerInline(generic.GenericTabularInline):
    model = InstantMessenger
    extra = 1

class StreetAddressInline(generic.GenericTabularInline):
    model = StreetAddress
    extra = 1

class WebSiteInline(generic.GenericTabularInline):
    model = WebSite
    extra = 1

class UserAdmin(admin.ModelAdmin):
    inlines = [PhoneNumberInline,
            InstantMessengerInline,
            StreetAddressInline,
            WebSiteInline,
    ]
    
class ListingInline(admin.TabularInline):
    model = Listing
    exclude = ('numBidders','date_closed','date_withdrawn','date_aborted')
    extra = 1

# Product Listing Admin for when adding listing. Sets the listing seller as the current logged in seller.
class PLAdmin(admin.ModelAdmin): 
    inlines = [ListingInline,]
    exclude = ('seller',)

    #sets product seller to be current logged in user
    def save_model(self, request, Product, form, change):
        Product.seller = Seller.objects.get(user = request.user)
        Product.save()

# For when adding ProductRequest. Sets user as current logged in user.
class ProductRequestAdmin(admin.ModelAdmin):
    exclude = ('user',)
    def save_model(self, request, ProductRequest, form, change):
        ProductRequest.user = User.objects.get(username = request.user.username)
        ProductRequest.save()
        
admin.site.register(Product, PLAdmin)
admin.site.register(Category)
admin.site.register(Seller, UserAdmin)
#admin.site.register(Listing)
admin.site.register(Bank)
admin.site.register(Escrow)
admin.site.register(BankAccount)
admin.site.register(Buyer, UserAdmin)
admin.site.register(ProductRequest, ProductRequestAdmin)
admin.site.register(Order)
admin.site.register(Cart)
