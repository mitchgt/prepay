from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group  ####Jennifer
from prepay.forms import LoginForm, RegistrationForm, ListingCommentForm #####Jennifer
from django.shortcuts import render_to_response  # ##Jennifer
from django.http import HttpResponseRedirect  ####Jennifer
from django.template import RequestContext  # ##Jennifer
from django.db import models  # ##Jennifer

from prepay.models import Listing, Category, UserProfile, Seller, Buyer, ProductRequest,Listing_Comment  # ##Jennifer edited
from django.contrib.auth import authenticate, login, logout##Lara
from django.contrib.auth.decorators import login_required##Lara
from django.core.urlresolvers import reverse##Lara
from django.utils import timezone

'''
####Jennifer new
def profile(request, user_username):
    user = get_object_or_404(User, username=user_username)
    if(Seller.objects.filter(username = user_username).exists()):
        return render(request, 'prepay/profile_seller.html', {'user':user})
    else:
        return render(request, 'prepay/profile_buyer.html', {'user':user})
#####Jennifer new
'''


def profile(request, user_username):
    if(Seller.objects.filter(username = user_username).exists()):
        user = get_object_or_404(Seller, username=user_username)
        return render(request, 'prepay/profile_seller.html', {'user':user})
    else:
        user = get_object_or_404(Buyer, username=user_username)
        return render(request, 'prepay/profile_buyer.html', {'user':user})
        
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
	if request.user.is_authenticated():
		return HttpResponseRedirect('/browse_listings')
	else:
		form = LoginForm()
		context = Context({
		'form':form
	})
		
		if request.method =='POST':
			form = LoginForm(request.POST)
			if form.is_valid():
				username = request.POST['username']
				password = request.POST['password']
				user = authenticate(username=username, password=password)
				if user is not None:
					if user.is_active:
						login(request, user)
						return HttpResponseRedirect('/browse_listings')
					else:
		          # Return a 'disabled account' error message
						return render(request, 'prepay/home.html', context)
				else:
        	# Return an 'invalid login' error message.
					return render(request, 'prepay/home.html', context)
		return render(request, 'prepay/home.html',context)



def about(request):
    return render(request, 'prepay/about.html')

'''
todo: 
refactor this to support browse by different criteria e.g. category
for now, created redundant browse_category
'''
@login_required
def browse_listings(request):
	login_flag=login_check(request)	
	all_listings = Listing.objects.all().order_by('-created_at')
	context = Context({
		'all_listings': all_listings,
		'login_flag':login_flag
	})
	return render(request, 'prepay/browse_listings.html',context)


@login_required
def browse_product_requests(request):
	login_flag=login_check(request)
	all_product_requests = ProductRequest.objects.all()
	context = Context({
		'all_product_requests': all_product_requests,
		'login_flag':login_flag
	})
	return render(request, 'prepay/browse_product_requests.html', context)

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
@login_required
def browse_category(request, category_id):
	login_flag=login_check(request)
	category = Category.objects.filter(pk=category_id)
	listings_by_category = Listing.objects.filter(product__categories__exact=category_id)
	context = Context({
		'category': category[0],
		'listings_by_category': listings_by_category,
		'login_flag':login_flag
	})
	return render(request, 'prepay/category.html', context)

@login_required
def listing_detail(request, listing_id):
    # return HttpResponse("You're looking at the detailed view of listing %s." % listing_id)
	login_flag=login_check(request)
	listing = get_object_or_404(Listing, pk=listing_id)
	if request.method =='POST':
		form = ListingCommentForm(request.POST,request.FILES)
		if form.is_valid():
			comment = request.POST.get('comment')
			rating = request.POST.get('rating')
			image = request.FILES.get('image')
			date = timezone.now()
			username=request.user.username
			User_Profile=get_object_or_404(UserProfile, username=username)
			Listing_Comment.objects.create(listing=listing,commenter=User_Profile,comment=comment, rating = rating,  date=date, image=image)

	form = ListingCommentForm()
	context = Context({
		'listing':listing,
		'form':form,
		'login_flag':login_flag
	})
	return render(request, 'prepay/detail.html',context)

def login_check(request):
	if request.user.is_authenticated():
		login_flag=1
	else:
		login_flag=0
	return login_flag
