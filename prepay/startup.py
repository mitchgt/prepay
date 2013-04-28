from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from prepay.models import Seller, Buyer


def set_groups():
       
    existing_groups = Group.objects.all()
    existing_permissions = Permission.objects.all()
        
    if not existing_groups.filter(name='Buyer'): 
        buyer_users = Group(name='Buyer')
        buyer_users.save()
        #buyer_users.permissions = [can_add_category, can_add_listing_comment, can_add_product_request, can_add_review]
        buyer_users.permissions.add(
            existing_permissions.get(codename = 'add_category'),
            existing_permissions.get(codename = 'add_productrequest'),
            existing_permissions.get(codename = 'add_productrequest'),
            existing_permissions.get(codename = 'change_productrequest'),
            existing_permissions.get(codename = 'delete_productrequest'),
        )
        buyer_users.save()
        
    if not existing_groups.filter(name='Seller'): 
        seller_users = Group(name='Seller')
        seller_users.save()
        #seller_users.permissions = [can_add_category, can_add_listing, can_add_listing_comment, can_add_product, can_add_product_request]
        seller_users.permissions.add(
            existing_permissions.get(codename = 'add_category'),
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

def create_default_users():
    existing_users = User.objects.all()
    
    if not existing_users.filter(username='joeseller'):
        acttype = 'Seller'
        #u = Seller.objects.create_user(new_data['username'], new_data['email'], new_data['password'])
        u = Seller.objects.create_user('joeseller', 'joe@whitehouse.gov', 'joe')
        '''
        u = Seller.objects.create_user(
                    username = 'joeseller',
                    first_name = 'Joe',
                    last_name = 'Seller',
                    email = 'joe@whitehouse.gov',
                    password = 'joe',
        )
        '''
        u.groups.add(Group.objects.get(name = acttype))
        u.is_staff = True
        u.slug = u.username
        u.save()
        u.bankaccount_set.create(name = u.username, user = u, balance = 0)
    
    if not existing_users.filter(username='joebuyer'):
        acttype = 'Buyer'
        u = Buyer.objects.create_user('joebuyer', 'joe@buyers.net', 'joe')
        u.groups.add(Group.objects.get(name = acttype))
        u.is_staff = True
        u.slug = u.username
        u.save()
        u.bankaccount_set.create(name = u.username, user = u, balance = 0)
    
