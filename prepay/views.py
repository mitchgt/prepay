from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group  ####Jennifer
from prepay.forms import LoginForm, RegistrationForm, ListingCommentForm, EditProfileForm, PhoneNumberFormSet, InstantMessengerFormSet, WebSiteFormSet, StreetAddressFormSet, SearchForm, CheckoutForm #####Jennifer
from django.shortcuts import render_to_response  # ##Jennifer
from django.http import HttpResponseRedirect  ####Jennifer
from django.template import RequestContext  # ##Jennifer
from django.db import models  # ##Jennifer

from prepay.models import Listing, Category, UserProfile, Seller, Buyer, ProductRequest,Listing_Comment, PhoneNumber, StreetAddress, WebSite, InstantMessenger, Product, Order, BankAccount, Escrow  # ##Jennifer edited
from django.contrib.auth import authenticate, login, logout##Lara
from django.contrib.auth.decorators import login_required##Lara
from django.core.urlresolvers import reverse##Lara
from django.utils import timezone
from django.shortcuts import redirect 
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
	if not request.user.username == user_username:
		return HttpResponseRedirect(reverse('prepay.views.profile', args=(user_username,)))
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
    login_flag=login_check(request)
    mine = False
    if(Seller.objects.filter(username = user_username).exists()):
        user = get_object_or_404(Seller, username=user_username)
        products = Product.objects.filter(seller = user)
        listings = Listing.objects.filter(product__seller = user)
        if request.user.username == user_username:
    		mine = True
        return render(request, 'prepay/profile_seller.html', {'theuser':user, 'products':products, 'listings':listings, 'mine':mine, 'login_flag': login_flag})
    else:
        user = get_object_or_404(Buyer, username=user_username)
        if request.user.username == user_username:
			mine = True
        return render(request, 'prepay/profile_buyer.html', {'theuser':user, 'mine':mine, 'login_flag': login_flag})

        
####Jennifer
def register(request):
    login_flag=login_check(request)
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
                u.bankaccount_set.create(name = u.username, user = u, balance = 0)
                return HttpResponseRedirect(reverse('browse_listings'))
            else:
                return render_to_response('prepay/register.html', {'form':form,'error':True, 'login_flag': login_flag}, context_instance=RequestContext(request))
    else:
        form = RegistrationForm()
    return render_to_response('prepay/register.html',{'form':form, 'login_flag': login_flag},context_instance=RequestContext(request))
####Jennifer



def index(request):
    if request.user.is_authenticated():
		#return HttpResponseRedirect('/browse_listings')
        return HttpResponseRedirect(reverse('browse_listings'))
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
						return HttpResponseRedirect(reverse('browse_listings'))
					else:
		          # Return a 'disabled account' error message
						return render(request, 'prepay/home.html', context)
				else:
        	# Return an 'invalid login' error message.
					return render(request, 'prepay/home.html', context)
		return render(request, 'prepay/home.html',context)


def about(request):
    login_flag=login_check(request)
    return render(request, 'prepay/about.html', {'login_flag':login_flag})

@login_required
def browse_listings(request):
	login_flag=login_check(request)	
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
			return render_to_response('prepay/browse_listings.html',{'all_listings':all_listings, 'form':form, 'login_flag':login_flag }, 
                                      context_instance=RequestContext(request)) 
	elif request.method == 'GET':    	
		if 'sort' in request.GET and request.GET['sort']:
			all_listings = request.session.get('last_listings')
			keywords = request.session.get('oldq')
			form = SearchForm(initial = {'q':keywords})	
			if request.GET['sort']=="Date posted":
				all_listings = all_listings.order_by('-created_at')
			elif request.GET['sort']=="Seller":
				all_listings = all_listings.order_by('-product__seller__username')
			elif request.GET['sort']=="Price - lowest to highest":
				all_listings = all_listings.order_by('-price').reverse()
			elif request.GET['sort']=="Price - highest to lowest":
				all_listings = all_listings.order_by('-price')
			elif request.GET['sort']=="Status":
				all_listings = all_listings.order_by('-status')
			elif request.GET['sort']=="Deadline for bidding":
				all_listings = all_listings.order_by('-deadlineBid').reverse()
			selected = request.GET['sort']
			return render_to_response('prepay/browse_listings.html',{'all_listings':all_listings, 'form':form, 'login_flag':login_flag, 'selected':selected }, 
                                      context_instance=RequestContext(request))
	all_listings = Listing.objects.all().order_by('-created_at')
	form = SearchForm()	
	request.session['last_listings']=all_listings
	request.session['oldq']=None
	context = Context({
        'all_listings': all_listings, 'form':form, 'login_flag':login_flag 
	})
	return render(request, 'prepay/browse_listings.html', context)



@login_required
def browse_product_requests(request):
	login_flag=login_check(request)
	all_product_requests = ProductRequest.objects.all()
	context = Context({
		'all_product_requests': all_product_requests,
		'login_flag':login_flag
	})
	return render(request, 'prepay/browse_product_requests.html', context)


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
	buyer = False
	goalreached = True
	if Buyer.objects.filter(username = request.user.username):
		buyer = True
	if listing.numBidders<listing.maxGoal:
		goalreached = False
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
			return HttpResponseRedirect(reverse("prepay.views.listing_detail", args=(listing.id,)))
	form = ListingCommentForm()
	context = Context({
		'listing':listing,
		'form':form,
		'login_flag':login_flag,
		'isBuyer':buyer,
		'goalreached':goalreached
	})
	return render(request, 'prepay/detail.html',context)

def login_check(request):
	if request.user.is_authenticated():
		login_flag=1
	else:
		login_flag=0
	return login_flag


def confirmed(request):
	login_flag=login_check(request)
	total = request.session['total']
	return render(request, 'prepay/confirmed.html',{'login_flag':login_flag, 'total':total})

def checkout(request, listing_id):
	login_flag=login_check(request)
	
	listing = Listing.objects.get(pk = listing_id)
	error = False ###
	exceed = False
	if listing.status != "Open for bidding" or not Buyer.objects.filter(username = request.user.username):
		return HttpResponseRedirect(reverse('prepay.views.listing_detail', args=(listing_id)))
	form = CheckoutForm()
	address_formset = StreetAddressFormSet()
	if request.method=='POST':
		form=CheckoutForm(request.POST)
		address_formset = StreetAddressFormSet(request.POST, instance = request.user)
		if form.is_valid() and address_formset.is_valid():
			if 'quantity' in request.POST:
				quantity = int(request.POST.get('quantity'))
				a = listing.numBidders + quantity
				buyer=Buyer.objects.get(username = request.user.username)
				total = quantity * listing.price 
				ba = BankAccount.objects.get(user = request.user)
				if ba.balance>=total and listing.maxGoal>=a:
					seller=listing.product.seller
					address=address_formset.save()
					for i in range(quantity):
						neworder = Order.objects.create(seller=seller, buyer=buyer, listing=listing)
						neworder.shipping_address = address
					listing.numBidders = a
					listing.save()
					ba.balance = ba.balance - total
					ba.save()
					e = Escrow.objects.get(listing=listing)
					e.balance = e.balance + total
					e.save()
					request.session['total']=total
					return HttpResponseRedirect(reverse("prepay.views.confirmed"))
				elif ba.balance>=total and listing.maxGoal<a:
					exceed = listing.maxGoal - listing.numBidders
				else:
					error = True

	return render_to_response('prepay/checkout.html',{'a_formset':address_formset, 'form':form, 'login_flag':login_flag, 'listing':listing, 'error':error, 'exceed':exceed }, context_instance=RequestContext(request))
