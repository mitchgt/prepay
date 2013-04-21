from django.contrib import admin
from prepay.models import Product, Category, Seller, Listing, Bank, Escrow, BankAccount, Buyer, ProductRequest, BankAccount, PhoneNumber, InstantMessenger, StreetAddress, WebSite, Order
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
    exclude = ('numBidders',)
    extra = 1

class PLAdmin(admin.ModelAdmin): 
    inlines = [ListingInline,]
    exclude = ('seller',)

    #sets product seller to be current logged in user
    def save_model(self, request, Product, form, change):
        Product.seller = Seller.objects.get(user = request.user)
        Product.save()


admin.site.register(Product, PLAdmin)
admin.site.register(Category)
admin.site.register(Seller, UserAdmin)
#admin.site.register(Listing)
admin.site.register(Bank)
admin.site.register(Escrow)
admin.site.register(BankAccount)
admin.site.register(Buyer, UserAdmin)
admin.site.register(ProductRequest)
admin.site.register(Order)
