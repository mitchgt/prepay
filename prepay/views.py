from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group  ####Jennifer
from prepay.forms import RegistrationForm  #####Jennifer
from django.shortcuts import render_to_response  # ##Jennifer
from django.http import HttpResponseRedirect  ####Jennifer
from django.template import RequestContext  # ##Jennifer
from django.db import models  # ##Jennifer

from prepay.models import Listing, Category, Seller, Buyer  # ##Jennifer edited

####Jennifer new
def profile(request, user_username):
    user = get_object_or_404(User, username=user_username)
	if(Seller.objects.filter(username = user_username).exists()):
		return render(request, 'prepay/profile_seller.html', {'user':user})
	else:
		return render(request, 'prepay/profile_buyer.html', {'user':user})
#####Jennifer new
        
####Jennifer
def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        new_data = request.POST.copy()
        if form.is_valid():
            username1 = request.POST.get('username')
            if not User.objects.filter(username = username1).exists():
                acttype = request.POST.get('account_type')
                if acttype == 'Seller':
                    u = Seller.objects.create_user(new_data['username'], new_data['email'], new_data['password'])
                elif acttype == 'Buyer':
                    u = Buyer.objects.create_user(new_data['username'], new_data['email'], new_data['password'])
                u.groups.add(Group.objects.get(name = acttype))
                u.is_staff = True
                u.save()
                return HttpResponseRedirect('/')
            else:
                return render_to_response('prepay/register.html',{'form':form,'error':True}, context_instance=RequestContext(request))
    else:
        form = RegistrationForm()
    return render_to_response('prepay/register.html',{'form':form},context_instance=RequestContext(request))
####Jennifer

def index(request):
    return render(request, 'prepay/home.html')

def about(request):
    return render(request, 'prepay/about.html')

'''
todo: 
refactor this to support browse by different criteria e.g. category
for now, created redundant browse_category
'''
def browse(request):
    all_listings = Listing.objects.all().order_by('-created_at')
    context = Context({
        'all_listings': all_listings,
    })
    return render(request, 'prepay/browse.html', context)

'''
Pretty sick how this:

select prepay_listing.name, prepay_product.name, prepay_category.name
from prepay_product, prepay_category, prepay_product_categories, prepay_listing
where prepay_product.id = prepay_product_categories.product_id
and prepay_product.id = prepay_listing.product_id
and prepay_category.id = prepay_product_categories.category_id
and prepay_category.id = 1

equals this:

Listing.objects.filter(product__category__exact=cat_id)

'''
def browse_category(request, category_id):
    category = Category.objects.filter(pk=category_id)
    listings_by_category = Listing.objects.filter(product__categories__exact=category_id)
    context = Context({
        'category': category[0],
        'listings_by_category': listings_by_category,
    })
    return render(request, 'prepay/category.html', context)

def listing_detail(request, listing_id):
    # return HttpResponse("You're looking at the detailed view of listing %s." % listing_id)
    listing = get_object_or_404(Listing, pk=listing_id)
    return render(request, 'prepay/detail.html', {'listing':listing})
