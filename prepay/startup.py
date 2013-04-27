from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def set_groups():
       
    existing_groups = Group.objects.all()
    existing_permissions = Permission.objects.all()
        
    if not existing_groups.filter(name='Buyer'): 
        buyer_users = Group(name='Buyer')
        buyer_users.save()
        #buyer_users.permissions = [can_add_category, can_add_listing_comment, can_add_product_request, can_add_review]
        buyer_users.permissions.add(
            existing_permissions.get(codename = 'add_category'),
            existing_permissions.get(codename = 'add_listing_comment'),
            existing_permissions.get(codename = 'add_productrequest'),
            existing_permissions.get(codename = 'add_productrequest'),
            existing_permissions.get(codename = 'change_productrequest'),
            existing_permissions.get(codename = 'delete_productrequest'),
            existing_permissions.get(codename = 'add_review'),
        )
        buyer_users.save()
        
    if not existing_groups.filter(name='Seller'): 
        seller_users = Group(name='Seller')
        seller_users.save()
        #seller_users.permissions = [can_add_category, can_add_listing, can_add_listing_comment, can_add_product, can_add_product_request]
        seller_users.permissions.add(
            existing_permissions.get(codename = 'add_category'),
            existing_permissions.get(codename = 'add_listing_comment'),
            existing_permissions.get(codename = 'add_listing'),
            existing_permissions.get(codename = 'change_listing'),
            existing_permissions.get(codename = 'delete_listing'),
            existing_permissions.get(codename = 'add_product'),
            existing_permissions.get(codename = 'change_product'),
            existing_permissions.get(codename = 'delete_product'),
            existing_permissions.get(codename = 'add_productrequest'),
            existing_permissions.get(codename = 'change_productrequest'),
            existing_permissions.get(codename = 'delete_productrequest'),
            existing_permissions.get(codename = 'add_review'),
        )        
        seller_users.save()

    
    
