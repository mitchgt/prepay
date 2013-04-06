from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group  ####Jennifer
from prepay.forms import LoginForm, RegistrationForm, ListingCommentForm #####Jennifer
from django.shortcuts import render_to_response  # ##Jennifer
from django.http import HttpResponseRedirect  ####Jennifer
from django.template import RequestContext  # ##Jennifer
from django.db import models  # ##Jennifer

from prepay.models import Listing, Category, Seller, Buyer, ProductRequest  # ##Jennifer edited
from django.contrib.auth import authenticate, login, logout##Lara

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
    if request.method == 'POST':
		if 'logout' in request.POST:
			logout(request)
	if request.user.is_authenticated():
		login_flag=1
		return render(request, 'prepay/browse_listings.html',{'login_flag':login_flag})
	else:
		login_flag=0
		form = LoginForm()
		if request.method =='POST':
			form1 = LoginForm(request.POST)
			if form1.is_valid():
				username = request.POST['username']
				password = request.POST['password']
				user = authenticate(username=username, password=password)
				if user is not None:
					if user.is_active:
						login(request, user)
						login_flag=1
						return render(request, 'prepay/browse_listings.html',{'login_flag':login_flag})
					else:
		          # Return a 'disabled account' error message
						return render(request, 'prepay/home.html', {'form':form,'login_flag':login_flag})
				else:
        	# Return an 'invalid login' error message.
					return render(request, 'prepay/home.html', {'form':form,'login_flag':login_flag})
		return render(request, 'prepay/home.html',{'login_flag':login_flag,'form':form})


def about(request):
    return render(request, 'prepay/about.html')

'''
todo: 
refactor this to support browse by different criteria e.g. category
for now, created redundant browse_category
'''
def browse_listings(request):
    all_listings = Listing.objects.all().order_by('-created_at')
    context = Context({
        'all_listings': all_listings,
    })
    return render(request, 'prepay/browse_listings.html', context)

def browse_product_requests(request):
    all_product_requests = ProductRequest.objects.all()
    context = Context({
        'all_product_requests': all_product_requests,
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
	if request.method =='POST':
		form = CommentForm(request.POST,request.FILES)
		if form.is_valid():
			comment = request.POST.get('comment')
			rating = request.POST.get('rating')
			image = request.FILES.get('image')
			listing.Listing_Comment_set.create(comment=comment, rating = rating,  date=date, image=image, )

	form = ListingCommentForm()
	return render(request, 'prepay/detail.html', {'listing':listing,'form':form})

