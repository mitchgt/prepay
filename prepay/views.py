from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group  ####Jennifer
from prepay.forms import LoginForm, RegistrationForm, ListingCommentForm, EditProfileForm, PhoneNumberFormSet, InstantMessengerFormSet, WebSiteFormSet, StreetAddressFormSet, SearchForm #####Jennifer
from django.shortcuts import render_to_response  # ##Jennifer
from django.shortcuts import redirect
from django.http import HttpResponseRedirect  ####Jennifer
from django.template import RequestContext  # ##Jennifer
from django.db import models  # ##Jennifer

from prepay.models import Listing, Category, Seller, Buyer, ProductRequest, PhoneNumber, StreetAddress, WebSite, InstantMessenger, Product  # ##Jennifer edited
from django.contrib.auth import authenticate, login, logout##Lara
from django.db.models import Q
from django.core.urlresolvers import reverse

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

def edit_profile(request, user_username):
	if (Seller.objects.filter(username = user_username).exists()):
		user = get_object_or_404(Seller, username=user_username)
	else:
		user = get_object_or_404(Buyer, username=user_username)
	phone_formset = PhoneNumberFormSet(instance=user)
	im_formset = InstantMessengerFormSet(instance=user)
	website_formset = WebSiteFormSet(instance=user)
	address_formset = StreetAddressFormSet(instance=user)
	form = EditProfileForm(instance = user)

	if request.method=='POST':
		form = EditProfileForm(request.POST, request.FILES, instance=user)
		phone_formset = PhoneNumberFormSet(request.POST, instance=user)
		im_formset = InstantMessengerFormSet(request.POST, instance=user)
		website_formset = WebSiteFormSet(request.POST, instance=user)
		address_formset = StreetAddressFormSet(request.POST, instance=user)

		if form.is_valid() and phone_formset.is_valid() and im_formset.is_valid() and website_formset.is_valid() and address_formset.is_valid():
			form.save()
			phone_formset.save()
			im_formset.save()
			website_formset.save()
			address_formset.save()
			return HttpResponseRedirect(reverse('prepay.views.profile', args=(user_username,)))
		else:
			return render_to_response('prepay/edit_profile.html',{'form':form, 'p_formset': phone_formset, 'i_formset': im_formset,'w_formset': website_formset, 's_formset': address_formset, 'Error': True, 'user':user},context_instance=RequestContext(request))

	return render_to_response('prepay/edit_profile.html',{'form':form, 'p_formset': phone_formset, 'i_formset': im_formset,'w_formset': website_formset, 's_formset': address_formset, 'user':user},context_instance=RequestContext(request))


def profile(request, user_username):
    if(Seller.objects.filter(username = user_username).exists()):
        user = get_object_or_404(Seller, username=user_username)
        products = Product.objects.filter(seller = user)
        return render(request, 'prepay/profile_seller.html', {'user':user, 'products':products})
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
                u.slug = username1
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

#def index(request):
def browse_listings(request):
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
    if request.method =='POST':
		form = SearchForm(request.POST)
		if form.is_valid:
			keywords=request.POST.get('q')
			form = SearchForm(request.POST, initial = {'q':keywords})
			query = Q()
			for term in keywords.split():
				q = Q(name__icontains=term) | Q(description__icontains=term) | Q(product__name__icontains=term) | Q(product__description__icontains=term) | Q(product__seller__username__icontains=term)
				query = query & q
			all_listings = Listing.objects.all().filter(query).order_by('-created_at')
			request.session['last_listings']=all_listings
			request.session['oldq']=keywords
			return render_to_response('prepay/browse_listings.html',{'all_listings':all_listings, 'form':form}, 
                                      context_instance=RequestContext(request)) 
    elif request.method == 'GET':    	
		if 'sort' in request.GET and request.GET['sort']:
			all_listings = request.session.get('last_listings')
			keywords = request.session.get('oldq')
			form = SearchForm(initial = {'q':keywords})	
			if request.GET['sort']=="1":
				all_listings = all_listings.order_by('-created_at')
			elif request.GET['sort']=="2":
				all_listings = all_listings.order_by('-product__seller__username')
			return render_to_response('prepay/browse_listings.html',{'all_listings':all_listings, 'form':form}, 
                                      context_instance=RequestContext(request))
    all_listings = Listing.objects.all().order_by('-created_at')
    form = SearchForm()	
    request.session['last_listings']=all_listings
    request.session['oldq']=None
    context = Context({
        'all_listings': all_listings, 'form':form
	})
    return render(request, 'prepay/browse_listings.html', context)

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

