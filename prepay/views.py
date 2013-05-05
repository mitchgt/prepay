from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from prepay.forms import LoginForm, RegistrationForm, ListingCommentForm, EditProfileForm
from prepay.forms import PhoneNumberFormSet, InstantMessengerFormSet, WebSiteFormSet, StreetAddressFormSet, StreetAddressFormSet2
from prepay.forms import SearchForm, CheckoutForm, ReviewForm
from django.shortcuts import render_to_response 
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.db import models
from prepay.models import Listing, Category, UserProfile, Seller, Buyer, ProductRequest
from prepay.models import Listing_Comment, PhoneNumber, StreetAddress, WebSite, InstantMessenger
from prepay.models import Product, Order, BankAccount, Escrow, Review, Cart
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.shortcuts import redirect 
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from datetime import timedelta
from django.core.exceptions import PermissionDenied
import random, string



# AUX function. Returns the BankAccount balance of user.
# To be used in mostly all views to display balance next to username
def get_user_balance(user):
    try:
        bankaccount = BankAccount.objects.get(user = user)
        return str(bankaccount.balance)
    except BankAccount.DoesNotExist:
        return ''

# AUX function. Sends confirmation link to registering user
def send_registration_confirmation(user):
    #hostsite = 'http://mitchgt.com/prepay'
    hostsite = 'NAME_OF_HOSTSITE'
    p = UserProfile.objects.get(username=user.username)
    title = "Prepay account confirmation"
    content = "Here is your confirmation link for PrePay:\n\n" + hostsite + reverse('confirm_registration', args=(p.confirmation_code, user.username))
    send_mail(title, content, 'no.reply.prepay@gmail.com', [user.email], fail_silently=False)
    
# AUX function. Returns 1 if logged in, 0 otherwise.
def login_check(request):
    if request.user.is_authenticated():
        login_flag=1
    else:
        login_flag=0
    return login_flag

# AUX function. Returns True if current user is buyer account.
def seller_account_type(request):
    if request.user.is_authenticated():
        if Seller.objects.filter(username=request.user.username):
            return True
    else:
        return False
        

# AUX function. Returns True if current user is seller account.
def buyer_account_type(request):
    if request.user.is_authenticated():
        if Buyer.objects.filter(username=request.user.username):
            return True
    else:
        return False



# Landing page.
def index(request):
    # If logged in, set preliminary context vars for template rendering and show home
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
        context = {
            'login_flag': login_flag,
            'user_balance': user_balance,
        }
        return render(request, 'prepay/home.html', context)

    # Else, show login form
    else:
        form = LoginForm()
        context = {}
        context['form'] = form
        
        if request.method =='POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = request.POST['username']
                password = request.POST['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        login_flag=1
                        context = Context({
                            'login_flag':login_flag,
                        })
                        return HttpResponseRedirect(reverse('index'))
                    else:
                  # Return a 'disabled account' error message
                        return render(request, 'prepay/log-in.html', context)
                else:
            # Return an 'invalid login' error message.
                    error = True
                    return render(request, 'prepay/log-in.html', {'form':form, 'error':error})
            else:
                return render(request, 'prepay/log-in.html', {'form':form})
        return render(request, 'prepay/log-in.html',context)




# User registration. User becomes active after clicking confirmation link sent through email.
def register(request):
    login_flag=login_check(request)
    user_balance = ''
    if login_flag==1:
        user_balance = get_user_balance(request.user)
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
                u.is_active = False # must confirm
                u.slug = username1 
                u.bankaccount_set.create(name = u.username, user = u, balance = 0)
                u.save()
                p = UserProfile.objects.get(username=username1)
                # generate 33 character confirmation code
                p.confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
                p.save()
                # send confirmation code (aux method)
                send_registration_confirmation(u)
                return HttpResponseRedirect(reverse('confirmation_code_sent', args=(u.username,)))
            else:
                context = {
                    'form':form,
                    'error':True,
                    'login_flag': login_flag,
                    'user_balance': user_balance
                }
                return render_to_response('prepay/register.html', context, context_instance=RequestContext(request))
    else:
        form = RegistrationForm()
    context = {
        'form':form,
        'login_flag': login_flag,
        'user_balance': user_balance,
    }
    return render_to_response('prepay/register.html', context,context_instance=RequestContext(request))



# Display to user after sending confirmation code
def confirmation_code_sent(request, user_username):
    context={}
    try:
        user = User.objects.get(username=user_username)
        context['user'] = user
        if not user.is_active:
            context['not_active'] = 1
    except User.DoesNotExist:
        pass
    context['user_username'] = user_username
    return render_to_response('prepay/confirmation_code_sent.html', context, context_instance=RequestContext(request))



# Check if given confirmation_code and user's confirmation_code match
# Redirect to login if match. Else, redirect to error page
def confirm_registration(request, confirmation_code, user_username):
    try:
        user = User.objects.get(username=user_username)
        profile = UserProfile.objects.get(username=user_username)
        if profile.confirm_registration(confirmation_code):
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponseRedirect(reverse('invalid_confirmation', args=(confirmation_code, user_username)))
    except User.DoesNotExist or Profile.DoesNotExist:
        return HttpResponseRedirect(reverse('invalid_confirmation', args=(confirmation_code, user_username)))


# When given confirmation_code is incorrect for user, or if user does not exist.
def invalid_confirmation_code(request, confirmation_code, user_username):
    context = {
        'confirmation_code':confirmation_code,
        'user_username':user_username
    }
    return render_to_response('prepay/invalid_confirmation_code.html', context, context_instance=RequestContext(request))
    
def logout(request):
	return HttpResponseRedirect(reverse('index'))   

# View profile. If user is seller, show user's listings.
def profile(request, user_username):

    # Preliminary context vars for template rendering
    login_flag=login_check(request)
    user_balance = ''
    if login_flag==1:
        user_balance = get_user_balance(request.user)
        

    mine = False
    buyer = False
    if buyer_account_type(request):
        buyer = True
        
    if(Seller.objects.filter(username = user_username).exists()):
        user = get_object_or_404(Seller, username=user_username)
        products = Product.objects.filter(seller = user)
        listings = Listing.objects.filter(product__seller = user)
        if request.user.username == user_username:
            mine = True
        
        context = Context({
            'isBuyer': buyer,
            'theuser': user, 
            'products': products, 
            'listings': listings, 
            'mine': mine, 
            'login_flag': login_flag,
            'user_balance': user_balance
        })

        return render(request, 'prepay/profile_seller.html', context)
    else:
        user = get_object_or_404(Buyer, username=user_username)
        form = ReviewForm()
        if request.user.username == user_username:
            mine = True
        context = {
            'isBuyer':buyer,
            'theuser':user,
            'mine':mine,
            'login_flag': login_flag,
            'form': form,
            'user_balance': user_balance
        }
        return render(request, 'prepay/profile_buyer.html', context)


# Edit user profile
def edit_profile(request, user_username):

    # Preliminary context vars for template rendering
    login_flag=login_check(request)
    user_balance = ''
    if login_flag==1:
        user_balance = get_user_balance(request.user)

    # check current user is owner of profile
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

    context = {
        'form':form,
        'p_formset': phone_formset,
        'i_formset': im_formset,
        'w_formset': website_formset,
        's_formset': address_formset,
        'Error': True, 'user':user,
        'login_flag': login_flag,
        'user_balance': user_balance,
        }

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
            return render_to_response('prepay/edit_profile.html', context ,context_instance=RequestContext(request))

    context['user'] = user
    context['login_flag'] = login_flag
    return render_to_response('prepay/edit_profile.html', context, context_instance=RequestContext(request))



# Our about page.
def about(request):

    # Preliminary context vars for template rendering
    login_flag=login_check(request)
    user_balance = ''
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    buyer = False
    if buyer_account_type(request):
        buyer = True
    context = Context({
        'isBuyer': buyer,
        'login_flag':login_flag,
        'user_balance': user_balance,
    })
    
    return render(request, 'prepay/about.html', context)


# Browse product listings with search and sort features
@login_required
def browse_listings(request, fil = None):
    # Preliminary context vars for template rendering
    login_flag=login_check(request)
    user_balance = ''
    if login_flag==1:
        user_balance = get_user_balance(request.user)

    categories= Category.objects.all()
    all_listings = Listing.objects.all().order_by('-created_at')
    cart = None
    b = None
    
    buyer = False
    if buyer_account_type(request):
        buyer = True
        b = Buyer.objects.get(username = request.user.username)
        cart = b.cart
            
    if fil!=None:
        if fil =="biddable":
            all_listings = all_listings.filter(Q(status = "Open for bidding") |
                Q(status = "Maximum reached"))
        elif fil == "bidclosed":
            all_listings = all_listings.filter(Q(status = "In Production") | Q(status = "Shipped"))
        elif fil == "over":
            all_listings = all_listings.filter(Q(status = "Closed") | Q(status = "Aborted") | Q(status = "Withdrawn"))
    if request.method =='POST':
        form = SearchForm(request.POST)
        if form.is_valid:
            keywords=request.POST.get('q')
            form = SearchForm(request.POST, initial = {'q':keywords})
            query = Q()
            for term in keywords.split():
                q = Q(name__icontains=term) | Q(description__icontains=term) | Q(product__name__icontains=term) | Q(product__description__icontains=term) | Q(product__seller__username__icontains=term)
                query = query & q
            all_listings = all_listings.filter(query).order_by('-created_at')
            request.session['last_listings']=all_listings
            request.session['oldq']=keywords
            context = {
                'all_listings':all_listings,
                'form':form,
                'login_flag':login_flag,
                'categories':categories,
                'filter':fil,
                'user_balance':user_balance,
                }
            return render_to_response('prepay/browse_listings.html',
                context,
                context_instance=RequestContext(request)) 
                
    elif request.method == 'GET':        
        if 'sort' in request.GET and request.GET['sort']:
            all_listings = request.session.get('last_listings')
            if fil =="biddable":
                all_listings = all_listings.filter(Q(status = "Open for bidding") | Q(status = "Maximum reached"))
            elif fil == "bidclosed":
                all_listings = all_listings.filter(Q(status = "In Production") | Q(status = "Shipped"))
            elif fil == "over":
                all_listings = all_listings.filter(Q(status = "Closed") | Q(status = "Aborted") | Q(status = "Withdrawn"))    
            keywords = request.session.get('oldq')
            form = SearchForm(initial = {'q':keywords})
            if request.GET['sort']=="Date posted":
                all_listings = all_listings.order_by('-created_at')
            elif request.GET['sort']=="Seller":
                all_listings = all_listings.order_by('product__seller__username')
            elif request.GET['sort']=="Price - low to high":
                all_listings = all_listings.order_by('price')
            elif request.GET['sort']=="Price - high to low":
                all_listings = all_listings.order_by('-price')
            elif request.GET['sort']=="Status":
                all_listings = all_listings.order_by('-status')
            elif request.GET['sort']=="Deadline for bidding":
                all_listings = all_listings.order_by('deadlineBid')
            selected = request.GET['sort']
            context = {
                'all_listings':all_listings,
                'form':form,
                'login_flag':login_flag,
                'selected':selected,
                'filter':fil,
                'categories':categories,
                'user_balance':user_balance
                }
            return render_to_response('prepay/browse_listings.html',
                context,
                context_instance=RequestContext(request))
    
    form = SearchForm()    
    request.session['last_listings']=all_listings
    request.session['oldq']=None
    context = Context({
        'all_listings': all_listings, 
        'form': form, 
        'login_flag': login_flag, 
        'filter': fil, 
        'categories': categories,
        'isBuyer': buyer,
        'cart': cart,
        'buyer': b,
        'user_balance': user_balance,
    })
    return render(request, 'prepay/browse_listings.html', context)



# Browse product requests
@login_required
def browse_product_requests(request):
    login_flag=login_check(request)
    user_balance = ''
    if login_flag:
        user_balance = get_user_balance(request.user)
    buyer = False
    if buyer_account_type(request):
        buyer = True
        
    all_product_requests = ProductRequest.objects.all()
    context = Context({
        'all_product_requests': all_product_requests,
        'login_flag': login_flag,
        'isBuyer': buyer,
        'user_balance': user_balance,
    })
    
    return render(request, 'prepay/browse_product_requests.html', context)


# Browse by category
@login_required
def browse_category(request, category_id):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    categories = Category.objects.all()
    category = Category.objects.filter(pk=category_id)
    listings_by_category = Listing.objects.filter(product__categories__exact=category_id)
    context = Context({
        'category': category[0],
        'listings_by_category': listings_by_category,
        'login_flag':login_flag,
        'categories':categories,
        'user_balance':user_balance
    })
    return render(request, 'prepay/category.html', context)


# Detailed view of listing
@login_required
def listing_detail(request, listing_id):

    # Preliminary context vars for template rendering
    login_flag=login_check(request)
    user_balance = ''
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    buyer = False
    b = None
    cart = None    
    if buyer_account_type(request):
        buyer = True
        b = Buyer.objects.get(username = request.user.username)
        cart = b.cart
    
    listing = get_object_or_404(Listing, pk=listing_id)
    goalreached = True
    if listing.numBidders<listing.maxGoal:
        goalreached = False
    
    if request.method =='POST':
        if 'shipped' in request.POST:
            listing.status = "Shipped"
            listing.save()
            orders = Order.objects.filter(listing = listing, status = "Ongoing")
            for order in orders:
                order.status = "Shipped"
                order.save()
            return HttpResponseRedirect(reverse("prepay.views.listing_detail", args=(listing.id,)))
        form = ListingCommentForm(request.POST,request.FILES)
        if form.is_valid():
            comment = request.POST.get('comment')
            rating = request.POST.get('rating')
            image = request.FILES.get('image')
            date = timezone.now()
            username=request.user.username
            User_Profile=get_object_or_404(UserProfile, username=username)
            Listing_Comment.objects.create(listing=listing,commenter=User_Profile,comment=comment, 
                                           rating = rating,  date=date, image=image)
            return HttpResponseRedirect(reverse("prepay.views.listing_detail", 
                    args=(listing.id,)))
            
    form = ListingCommentForm()
    
    context = Context({
        'listing': listing,
        'form': form,
        'login_flag': login_flag,
        'isBuyer': buyer,
        'goalreached': goalreached,
        'cart': cart,
        'user_balance': user_balance,
    })
    return render(request, 'prepay/detail.html',context)




# When user submits a review of product after receiving product
def review(request, order_id):

    # Preliminary context vars for template rendering
    login_flag=login_check(request)
    user_balance = ''
    if login_flag==1:
        user_balance = get_user_balance(request.user)


    buyer = False
    if buyer_account_type(request):
        buyer = True

    order = get_object_or_404(Order,pk=order_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            seller = order.listing.product.seller
            buyer = Buyer.objects.get(username = request.user.username)
            review = request.POST.get('review')
            rating = request.POST.get('rating')
            Review.objects.create(seller = seller, buyer = buyer, review = review, rating = rating, order = order)
            order.status = "Rated"
            order.save()
            count = Review.objects.filter(seller= seller).count()
            if seller.rating==None:
                seller.rating = rating
            elif count == 0:
                seller.rating = (seller.rating + rating)/2
            else:
                seller.rating = (seller.rating * count + int(rating))/(count+1)
            seller.save()
            context = {
                'login_flag':login_flag,
                'isBuyer': buyer,
                'user_balance':user_balance
            }
            return render(request, 'prepay/reviewed.html', context)
        else:
            error = True
            context = {
                'login_flag':login_flag,
                'error':error,
                'user_balance':user_balance
            }
            return render(request, 'prepay/reviewed.html',context)
    direct = True
    context = {
        'login_flag':login_flag,
        'direct':direct,
        'isBuyer':buyer,
        'user_balance': user_balance
    }
    return render(request, 'prepay/reviewed.html', context)


def confirmed(request):
    login_flag=login_check(request)
    user_balance = ''
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    total = request.session['total']
    prev_balance = request.session['prev_balance']
    ba = BankAccount.objects.get(user = request.user)
    context = {
        'login_flag':login_flag,
        'total':total,
        'prev_balance':prev_balance,
        'ba':ba,
        'user_balance':user_balance
    }
    return render(request, 'prepay/confirmed.html', context)

def checkout(request, listing_id):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    buyer = False
    if Buyer.objects.filter(username = request.user.username):
        buyer = True
    
    listing = get_object_or_404(Listing,pk = listing_id)
    error = False ###
    exceed = False
    if listing.status != "Open for bidding" or not Buyer.objects.filter(username = request.user.username):
        return HttpResponseRedirect(reverse('prepay.views.listing_detail', args=(listing_id)))
    form = CheckoutForm()
    address_formset = StreetAddressFormSet2()

    b = Buyer.objects.get(username = request.user.username)
    
    if request.method=='POST':
        form=CheckoutForm(request.POST)
        address_formset = StreetAddressFormSet2(request.POST, instance = request.user)
        if form.is_valid() and address_formset.is_valid():
            for i in address_formset:
                if i.has_changed():
                    break
                missing = True
                #address_formset = StreetAddressFormSet2()
                context = Context({'a_formset':address_formset,
                       'form':form, 
                       'login_flag':login_flag, 
                       'listing':listing, 
                       'missing':missing, 
                       'isBuyer':buyer,
                       'user_balance':user_balance
                       })

                return render(request, 'prepay/checkout.html', context)
            if 'quantity' in request.POST:
                quantity = int(request.POST.get('quantity'))
                a = listing.numBidders + quantity
                buyer=Buyer.objects.get(username = request.user.username)
                total = quantity * listing.price 
                ba = BankAccount.objects.get(user = request.user)
                if ba.balance>=total and listing.maxGoal>=a:
                    seller=listing.product.seller
                    for i in range(quantity):
                        neworder = Order.objects.create(seller=seller, buyer=buyer, listing=listing)
                        neworder.shipping_address = address_formset.save()
                        #remove from cart
                        b.cart.listings.remove(listing)
                        b.save()
                    listing.numBidders = a
                    listing.save()
                    prev_balance = ba.balance
                    ba.balance = ba.balance - total
                    ba.save()
                    e = Escrow.objects.get(listing=listing)
                    e.balance = e.balance + total
                    e.save()
                    request.session['prev_balance']=prev_balance
                    request.session['total']=total
                    return HttpResponseRedirect(reverse("prepay.views.confirmed"))
                elif ba.balance>=total and listing.maxGoal<a:
                    exceed = listing.maxGoal - listing.numBidders
                else:
                    error = True

    context = Context({'a_formset':address_formset, 
                       'form':form, 
                       'login_flag':login_flag, 
                       'listing':listing, 
                       'error':error, 
                       'exceed':exceed,
                       'isBuyer':buyer,
                       'user_balance':user_balance
                       })

    return render(request, 'prepay/checkout.html', context)

def withdraw(request, order_id):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    order = get_object_or_404(Order,pk=order_id)
    if order.buyer.username != request.user.username:
        return HttpResponseRedirect(reverse('prepay.views.profile', args=(request.user.username,)))
    if order.status == "Aborted by seller" or order.status =="Closed" or order.status == "Withdrawn" or order.status == "Returned":
        notongoing = True
        return render(request, 'prepay/withdraw.html',{'login_flag':login_flag, 'notongoing':notongoing, 'user_balance':user_balance})
    date = timezone.now()
    if date>=order.listing.deadlineBid:
        cannot = True
        return render(request, 'prepay/withdraw.html',{'login_flag':login_flag, 'cannot':cannot, 'user_balance':user_balance})
    else:
        if request.method=='POST':
            order.listing.numBidders = order.listing.numBidders-1
            order.listing.save()
            e = Escrow.objects.get(listing=order.listing)
            e.balance = e.balance - order.listing.price
            e.save()
            ba = BankAccount.objects.get(user = request.user)
            ba.balance = ba.balance + order.listing.price
            ba.save()
            order.status = "Withdrawn"
            order.date_withdrawn = date
            order.save()
            confirm = True
            points = order.listing.price
            if order.buyer.rating == None or order.buyer.rating == 0:
                order.buyer.rating = 0
            else:
                order.buyer.rating = order.buyer.rating - 1
            order.buyer.save()
            context = {
                'login_flag':login_flag,
                'order':order,
                'confirm':confirm,
                'points':points,
                'user_balance':user_balance
            }
            return render(request, 'prepay/withdraw.html', context)
    return render(request, 'prepay/withdraw.html',{'login_flag':login_flag, 'order':order, 'user_balance':user_balance})

def confirmreceipt(request, order_id):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    order = get_object_or_404(Order,pk=order_id)
    if order.buyer.username != request.user.username:
        return HttpResponseRedirect(reverse('prepay.views.profile', args=(request.user.username,)))
    if order.status == "Aborted by seller" or order.status =="Closed" or order.status == "Withdrawn" or order.status == "Returned":
        notongoing = True
        return render(request, 'prepay/confirmreceipt.html',{'login_flag':login_flag, 'notongoing':notongoing, 'user_balance':user_balance})
    else:
        date = timezone.now()
        if request.method=='POST':
            e = Escrow.objects.get(listing=order.listing)
            amount = order.listing.price/2
            e.balance = e.balance - amount
            e.save()
            ba = BankAccount.objects.get(user = order.listing.product.seller)
            ba.balance = ba.balance + amount
            ba.save()
            order.status = "Closed"
            order.date_delivered = date
            order.save()
            confirm = True
            if order.buyer.rating == None:
                order.buyer.rating = 5
            elif order.buyer.rating<5:
                order.buyer.rating = order.buyer.rating + 1
            order.buyer.save()
            context = {
                'login_flag':login_flag,
                'order':order,
                'confirm':confirm,
                'user_balance':user_balance
            }
            return render(request, 'prepay/confirmreceipt.html', context)
    context = {
        'login_flag':login_flag,
        'order':order,
        'user_balance':user_balance
    }
    return render(request, 'prepay/confirmreceipt.html', context)

def orders(request, listing_id):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    listing = get_object_or_404(Listing, pk=listing_id)
    mine = False
    if request.user.username == listing.product.seller.username:
        mine = True
    orders = Order.objects.filter(listing = listing)
    #return render_to_response('prepay/orders.html',{'listing':listing, 'orders':orders, 'mine':mine, 'login_flag': login_flag})
    context = {
        'listing':listing,
        'orders':orders,
        'mine':mine,
        'login_flag': login_flag,
        'user_balance':user_balance
    }
    return render(request, 'prepay/orders.html', context)

def withdrawListing(request, listing_id):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    listing = get_object_or_404(Listing, pk=listing_id)
    date = timezone.now()
    if listing.product.seller.username != request.user.username:
        return HttpResponseRedirect(reverse('prepay.views.profile', args=(request.user.username,)))
    if listing.status == "Aborted" or listing.status =="Closed" or listing.status == "Withdrawn":
        notongoing = True
        context = {
            'listing':listing,
            'login_flag':login_flag,
            'notongoing':notongoing,
            'user_balance':user_balance
        }
        return render(request, 'prepay/withdraw_listing.html', context)
    if date <= listing.deadlineBid and request.method!="POST":
        withdraw = True
        context = {
            'listing':listing,
            'withdraw':withdraw,
            'login_flag': login_flag,
            'user_balance':user_balance
        }
        return render(request, 'prepay/withdraw_listing.html', context)
    if date <= listing.deadlineDeliver and request.method!="POST":
        terminate = True
        context = {
            'listing':listing,
            'terminate':terminate,
            'login_flag': login_flag,
            'user_balance':user_balance
        }
        return render(request, 'prepay/withdraw_listing.html', context)
    else:
        if request.method == "POST":
            orders = Order.objects.filter(status = "Ongoing", listing = listing)
            e = Escrow.objects.get(listing=listing)
            for order in orders:
                ba = BankAccount.objects.get(user = order.buyer)
                ba.balance = ba.balance + listing.price
                ba.save()
                e.balance = e.balance - listing.price
                e.save()
                order.status = "Aborted by seller"
                order.date_aborted = date
                order.save()
            listing.status = "Withdrawn"
            listing.date_withdrawn = date
            listing.save()         
            confirm = True
            rating = listing.product.seller.rating
            if rating == None or rating == 0:
                listing.product.seller.rating = 0
            elif date<= listing.deadlineBid:
                listing.product.seller.rating = rating - 1
            else:
                if rating == 1:
                    listing.product.seller.rating = 0
                else:
                    listing.product.seller.rating = rating - 2
            listing.product.seller.save()
            context = {
                'listing':listing,
                'confirm':confirm,
                'login_flag': login_flag,
                'user_balance':user_balance
            }
            return render(request, 'prepay/withdraw_listing.html', context)
    context = {
        'listing':listing,
        'login_flag': login_flag,
        'user_balance':user_balance
    }
    return render(request, 'prepay/withdraw_listing.html', context)

def returns(request, order_id):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    date = timezone.now()
    order = get_object_or_404(Order,pk=order_id)
    if order.seller.username != request.user.username:
        return HttpResponseRedirect(reverse('prepay.views.profile', args=(request.user.username,)))
    if date >= (order.listing.deadlineDeliver+timedelta(weeks = 4)):
        return render(request, 'prepay/returns.html',{'login_flag':login_flag, 'over':True, 'user_balance':user_balance})
    if order.status == "Aborted by seller" or order.status == "Withdrawn" or order.status == "Returned":
        notongoing = True
        context = {
            'login_flag':login_flag,
            'notongoing':notongoing,
            'user_balance':user_balance
        }
        return render(request, 'prepay/returns.html', context)
    else:
        date = timezone.now()
        if request.method=='POST':
            e = Escrow.objects.get(listing=order.listing)
            amount = order.listing.price/2
            e.balance = e.balance - amount
            e.save()
            ba = BankAccount.objects.get(user = order.buyer)
            ba.balance = ba.balance + amount
            ba.save()
            order.status = "Returned"
            order.save()
            confirm = True
            if order.buyer.rating == None:
                order.buyer.rating = 5
            elif order.buyer.rating<5:
                order.buyer.rating = order.buyer.rating + 1
            order.buyer.save()
            context = {
                'login_flag':login_flag,
                'order':order,
                'confirm':confirm,
                'user_balance':user_balance
            }
            return render(request, 'prepay/returns.html', context)
    context = {
        'login_flag':login_flag,
        'order':order,
        'user_balance':user_balance
    }
    return render(request, 'prepay/returns.html', context)

def autoconfirm():
    listings = Listing.objects.filter(status = "Shipped")
    date = timezone.now()
    for listing in listings:
        if date >= (listing.deadlineDeliver+timedelta(weeks = 4)):
            orders = Order.objects.filter(status = "Shipped", listing = listing)
            e = Escrow.objects.get(listing=listing)
            for order in orders:
                order.status = "Closed"
                order.date_delivered = date
                order.save()
            amount = e.balance
            e.balance = 0
            e.save()
            ba = BankAccount.objects.get(user = listing.product.seller)
            ba.balance = ba.balance + amount
            ba.save()
            listing.status = "Closed"
    listings = Listing.objects.filter(status = "Withdrawn")
    for listing in listings:
        if date >= (listing.deadlineDeliver+timedelta(weeks = 4)):
            amount = e.balance
            e.balance = 0
            e.save()
            ba = BankAccount.objects.get(user = listing.product.seller)
            ba.balance = ba.balance + amount
            ba.save()
    listings = Listing.objects.filter(status = "Aborted")
    for listing in listings:
        if date >= (listing.deadlineDeliver+timedelta(weeks = 4)):
            amount = e.balance
            e.balance = 0
            e.save()
            ba = BankAccount.objects.get(user = listing.product.seller)
            ba.balance = ba.balance + amount
            ba.save()
    return

def updateStatus():
    listings = Listing.objects.all()
    date = timezone.now()
    for listing in listings:
        if listing.status =="Closed" or listing.status == "Withdrawn" or listing.status =="Aborted":
            continue
        if date < listing.deadlineBid:
            if numBidders == maxGoal and listing.status == "Open for bidding":
                listing.status = "Maximum reached"
                listing.save()
            elif numBidders<maxGoal and listing.status == "Maximum reached":
                listing.status = "Open for bidding"
                listing.save()
        elif date >= listing.deadlineBid and (listing.status =="Open for bidding" or listing.status == "Maximum reached"):
            if numBidders >= minGoal:
                listing.status = "In Production"
                listing.save()
            else:
                listing.status = "Aborted"
                listing.date_aborted = date
                refund(listing.id)
        elif date >= listing.deadlineDeliver and listing.status!= "Shipped":
            listing.status = "Aborted"
            if listing.product.seller.rating ==None or listing.product.seller.rating <2:
                listing.product.seller.rating ==0
                listing.product.seller.save()
            else:
                listing.product.seller.rating = listing.product.seller.rating -2
                listing.product.seller.save()
            listing.date_aborted = date
            refund(listing.id)
    return

def refund(listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    orders = Order.objects.filter(status = "Ongoing", listing = listing)
    e = Escrow.objects.get(listing = listing)
    for order in orders:
        e.balance = e.balance - listing.price
        e.save()
        ba = BankAccount.objects.get(user = order.buyer)
        ba.balance = ba.balance + listing.price
        ba.save()
    return

@login_required
def addtocart(request, listing_id):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    listing = get_object_or_404(Listing, pk=listing_id)
    buyer = False
    goalreached = True
    if Buyer.objects.filter(username = request.user.username):
        buyer = True
    if listing.numBidders<listing.maxGoal:
        goalreached = False
            
    b = Buyer.objects.get(username = request.user.username)
    
    if not b.cart:
        c = Cart(name=b.username + "'s cart")
        c.save()
        b.cart = c
        b.save()
    
    b.cart.listings.add(listing)
    b.save()
    
    context = Context({
        'login_flag': login_flag,
        'listings': b.cart.listings.all,
        'isBuyer': buyer,
        'user_balance':user_balance
    })
    return render(request, 'prepay/cart.html', context)

@login_required
def addtocart(request, listing_id):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    listing = get_object_or_404(Listing, pk=listing_id)
    buyer = False
    goalreached = True
    if Buyer.objects.filter(username = request.user.username):
        buyer = True
    if listing.numBidders<listing.maxGoal:
        goalreached = False
            
    b = Buyer.objects.get(username = request.user.username)
    
    if not b.cart:
        c = Cart(name=b.username + "'s cart")
        c.save()
        b.cart = c
        b.save()
    
    b.cart.listings.add(listing)
    b.save()
    
    context = Context({
        'login_flag': login_flag,
        'listings': b.cart.listings.all,
        'isBuyer': buyer,
        'user_balance':user_balance
    })
    return render(request, 'prepay/cart.html', context)

def removefromcart(request, listing_id):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    listing = get_object_or_404(Listing, pk=listing_id)
    buyer = False
    goalreached = True
    if Buyer.objects.filter(username = request.user.username):
        buyer = True
    if listing.numBidders<listing.maxGoal:
        goalreached = False
            
    b = Buyer.objects.get(username = request.user.username) 

    b.cart.listings.remove(listing)
    b.save()
    
    context = Context({
        'login_flag': login_flag,
        'listings': b.cart.listings.all,
        'isBuyer': buyer,
        'user_balance':user_balance
    })
    return render(request, 'prepay/cart.html', context)

@login_required
def viewcart(request):
    login_flag=login_check(request)
    if login_flag==1:
        user_balance = get_user_balance(request.user)
    buyer = False
    if Buyer.objects.filter(username = request.user.username):
        buyer = True
    
    b = Buyer.objects.get(username = request.user.username)
    
    listings = None
    if b.cart is not None:
        listings = b.cart.listings.all
    
    context = Context({
        'login_flag': login_flag,
        'isBuyer': buyer,
        'listings': listings,
        'user_balance':user_balance
    })
    return render(request, 'prepay/cart.html', context)
