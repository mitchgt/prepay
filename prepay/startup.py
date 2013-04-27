from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def set_groups():
    
    can_add_category = 'None'
    can_add_listing = 'None'
    can_add_listing_comment = 'None'
    can_add_product = 'None'
    can_add_product_request = 'None'
    can_add_review = 'None'
    
    #Define permissions
    if not Permission.objects.filter(codename='can_add_category'):
        category_ct = ContentType.objects.get(app_label='prepay', model='category')
        can_add_category = Permission(name='Can add category.', codename='can_add_category', content_type=category_ct)
        can_add_category.save()
    
    if not Permission.objects.filter(codename='can_add_listing'):
        listing_ct = ContentType.objects.get(app_label='prepay', model='listing')
        can_add_listing = Permission(name='Can add listing.', codename='can_add_listing', content_type=listing_ct)
        can_add_listing.save()

    if not Permission.objects.filter(codename='can_add_listing_comment'):    
        listing_comment_ct = ContentType.objects.get(app_label='prepay', model='listing_comment')
        can_add_listing_comment = Permission(name='Can add listing comment.', codename='can_add_listing_comment', content_type=listing_comment_ct)
        can_add_listing_comment.save()

    if not Permission.objects.filter(codename='can_add_product'):   
        product_ct = ContentType.objects.get(app_label='prepay', model='product')
        can_add_product = Permission(name='Can add product.', codename='can_add_product', content_type=product_ct)
        can_add_product.save()

    if not Permission.objects.filter(codename='can_add_product_request'):   
        product_request_ct = ContentType.objects.get(app_label='prepay', model='productrequest')
        can_add_product_request = Permission(name='Can add product request.', codename='can_add_product_request', content_type=product_request_ct)
        can_add_product_request.save()

    if not Permission.objects.filter(codename='can_add_review'):  
        review_ct = ContentType.objects.get(app_label='prepay', model='review')
        can_add_review = Permission(name='Can add review.', codename='can_add_review', content_type=review_ct)
        can_add_review.save()


    existing_groups = Group.objects.all()
        
    if not existing_groups.filter(name='Buyer'): 
        buyer_users = Group(name='Buyer')
        buyer_users.save()
        buyer_users.permissions = [can_add_category, can_add_listing_comment, can_add_product_request, can_add_review]
        buyer_users.save()
        
    if not existing_groups.filter(name='Seller'): 
        seller_users = Group(name='Seller')
        seller_users.save()
        seller_users.permissions = [can_add_category, can_add_listing, can_add_listing_comment, can_add_product, can_add_product_request]
        seller_users.save()

    
    
