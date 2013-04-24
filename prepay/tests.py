import datetime, urllib

from django.utils import timezone

from django.test import TestCase

from django.core.files import File
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User, Group

from prepay.models import Seller, Buyer, Product, Listing, Category

def create_seller():
    return Seller.objects.create_user('seller_username', 'seller_email', 'seller_password')

def create_buyer():
    return Buyer.objects.create_user('buyer_username', 'buyer_email', 'buyer_password')

def create_category():
    return Category.objects.create(name='some_category')

def create_listing():
    seller = create_seller()
    category = create_category()
    product = Product.objects.create(name='product_name', seller=seller, description='product_description', categories=category)    
    url = urllib.urlretrieve('http://digital-photography-school.com/wp-content/uploads/2013/03/Acorn256.png')
    product.picture.save('test_pic.jpg', File(open(url[0])))
    return Listing.objects.create(name='some_listing', price=1000, minGoal=1, maxGoal=4, deadlineBid=timezone.now() + datetime.timedelta(days=10), deadlineDeliver=timezone.now()+datetime.timedelta(days=20), product=product)










class ModelMethodTests(TestCase):

    def test_get_account_type(self):
        seller = create_seller()
        self.assertEqual(seller.get_account_type(), 'seller')

        buyer = create_buyer()
        self.assertEqual(buyer.get_account_type(), 'buyer')

class ViewsTestsBlankSite(TestCase):
    def test_index_view_no_login(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to PrePay")
        self.assertContains(response, "Username")
        self.assertContains(response, "Password")

    def test_browse_listings_view_no_login(self):
        response = self.client.get(reverse('browse_listings'))
        self.assertEqual(response.status_code, 302)

    def test_browse_product_requests_view_no_login(self):
        response = self.client.get(reverse('browse_product_requests'))
        self.assertEqual(response.status_code, 302)

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register now!")
        self.assertContains(response, "Username")
        self.assertContains(response, "Password")
        self.assertContains(response, "Account type")

    def test_submit_registration(self):
        response = self.client.post('/register', {'username': 'test', 'email': 'test@email.com', 'password': 'test', 'account_type': 'Seller'})
        self.assertEqual(response.status_code, 302)

