import datetime, urllib

from django.utils import timezone

from django.test import TestCase

from django.core.files import File
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User, Group

from prepay.models import Seller, Buyer, Product, Listing, Category




# Model creation methods
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







# Test model methods
class ModelMethodTests(TestCase):

    def test_get_account_type(self):
        seller = create_seller()
        self.assertEqual(seller.get_account_type(), 'seller')

        buyer = create_buyer()
        self.assertEqual(buyer.get_account_type(), 'buyer')





# Test POST requests
class PostTestsBlankSite(TestCase):
    fixtures = ['blank_site_testdata.json']

    # Test log in through POST
    # All logins other than this will be through TestCase.Client.login()
    def test_login_fail(self):
        response = self.client.post(reverse('index'), {'username': 'doesnotexist', 'password': 'doesnotexist'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Invalid login - Please try again.")

    def test_login_success(self):
        response = self.client.post(reverse('index'), {'username': 'testuser', 'password': 'testuser'}, follow=True)
        self.assertEquals(response.status_code, 200)
        logged_in_index_template(self, response, "testuser")

    # Test registration with POST
    def test_submit_seller_registration(self):
        response = self.client.post(reverse('register'), {'username': 'test', 'email': 'test@email.com', 'password': 'test', 'account_type': 'Seller'}, follow=True)
        self.assertEquals(response.status_code, 200)
        logged_in_index_template(self, response, "test")

    def test_submit_buyer_registration(self):
        response = self.client.post(reverse('register'), {'username': 'test', 'email': 'test@email.com', 'password': 'test', 'account_type': 'Buyer'}, follow=True)
        self.assertEquals(response.status_code, 200)
        logged_in_index_template(self, response, "test")








# Global aux function to avoid code duplication for templates testing
def logged_in_index_template(self, response, username):
    self.assertContains(response, username)
    self.assertContains(response, "change password")
    self.assertContains(response, "logout")
    self.assertContains(response, "No Listings are available.")


# Test templates
class TemplateTestsBlankSite(TestCase):
    fixtures = ['blank_site_testdata.json']

    def test_index_template_no_login(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to PrePay")
        self.assertContains(response, "Username")
        self.assertContains(response, "Password")

    def test_index_template_logged_in(self):
        self.assertTrue(self.client.login(username='testuser', password='testuser'))
        response = self.client.get(reverse('index'), follow=True)
        self.assertContains(response, "change password")
        self.assertContains(response, "logout")
        self.assertContains(response, "No Listings are available.")

    def test_browse_listings_template_no_login(self):
        response = self.client.get(reverse('browse_listings'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to PrePay")
        self.assertContains(response, "Username")
        self.assertContains(response, "Password")

    def test_browse_listings_template_logged_in(self):
        self.assertTrue(self.client.login(username='testuser', password='testuser'))
        response = self.client.get(reverse('browse_listings'), follow=True)
        self.assertContains(response, "change password")
        self.assertContains(response, "logout")
        self.assertContains(response, "No Listings are available.")

    def test_browse_product_requests_template_no_login(self):
        response = self.client.get(reverse('browse_product_requests'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to PrePay")
        self.assertContains(response, "Username")
        self.assertContains(response, "Password")

    def test_browse_product_requests_template_logged_in(self):
        self.assertTrue(self.client.login(username='testuser', password='testuser'))
        response = self.client.get(reverse('browse_product_requests'), follow=True)
        self.assertContains(response, "Browse Product Requests")
        self.assertContains(response, "No Listings are available.")

    def test_register_template(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register now!")
        self.assertContains(response, "Username")
        self.assertContains(response, "Password")
        self.assertContains(response, "Account type")




        # Test populating database through website

        

