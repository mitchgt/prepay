from django.contrib import admin
from prepay.models import Product, Category, Seller, Listing, Bank, Escrow, BankAccount, Buyer, ProductRequest

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Seller)
admin.site.register(Listing)
admin.site.register(Bank)
admin.site.register(Escrow)
admin.site.register(BankAccount)
admin.site.register(Buyer)
admin.site.register(ProductRequest)
