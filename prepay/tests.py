import datetime, urllib

from django.utils import timezone

from django.test import TestCase

from django.core.files import File
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User, Group

from prepay.models import Seller, Buyer, Product, Listing, Category, UserProfile




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

    def test_user_confirmation(self):
        user = create_buyer()
        user.confirmation_code = 'ABC123'
        self.assertFalse(user.confirm_registration('123abc'))
        self.assertTrue(user.confirm_registration('ABC123'))
        self.assertTrue(user.is_active)




# Test POST requests
class PostTestsBlankSite(TestCase):
    fixtures = ['blank_site_testdata.json']

    # Test log in through POST
    # All logins other than this will be through TestCase.Client.login()
    def test_login_fail(self):
        response = self.client.post(reverse('index'), {'username': 'doesnotexist', 'password': 'doesnotexist'}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Invalid login - Please try again!")

    def test_login_success(self):
        response = self.client.post(reverse('index'), {'username': 'testuser', 'password': 'testuser'}, follow=True)
        self.assertEquals(response.status_code, 200)
        logged_in_index_template(self, response, "testuser")

    # Test POST

    # Test valid registration for seller
    def test_seller_registration_success(self):
        username = 'test'
        email = 'test@email.com'
        password = 'testtest'
        confirm_password = 'testtest'
        account_type = 'Seller'

        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        profile = UserProfile.objects.get(username='test')
        self.assertTrue(profile)
        self.assertFalse(profile.is_active)

        self.assertTrue(profile.confirm_registration(profile.confirmation_code))
        self.assertTrue(profile.is_active)

    # Test valid registration for buyer
    def test_buyer_registration_success(self):
        username = 'test'
        email = 'test@email.com'
        password = 'testtest'
        confirm_password = 'testtest'
        account_type = 'Buyer'

        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        profile = UserProfile.objects.get(username='test')
        self.assertTrue(profile)
        self.assertFalse(profile.is_active)

        self.assertTrue(profile.confirm_registration(profile.confirmation_code))
        self.assertTrue(profile.is_active)

    # Test invalid registration. Start blank and gradually fill.
    def test_registration_fail(self):
        username = ''
        email = ''
        password = ''
        confirm_password = ''
        account_type = ''

        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This field is required.")


        # add username to form. Use superusername to check namespace conflict later.
        # expect 'field required' message
        username= 'wdkim'
        email = ''
        password = ''
        confirm_password = ''
        account_type = ''
        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This field is required.")


        # add invalid email to form
        # expect 'field required' message
        username= 'wdkim'
        email = 'email'
        password = ''
        confirm_password = ''
        account_type = ''
        
        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, "Enter a valid e-mail address.")


        # add valid email to form
        # expect 'field required' message
        email = 'test@email.com'
        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertNotContains(response, "Enter a valid e-mail address.")

        # add (short) password to form, but not confirm_password
        # expect 'field required' message
        username= 'wdkim'
        email = 'test@email.com'
        password='test'
        confirm_password = ''
        account_type = ''

        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This field is required.")

        # add mismatching confirm_password to form
        # expect 'field missing' because account_type is empty
        username= 'wdkim'
        email = 'test@email.com'
        password='test'
        confirm_password='testtttt'
        account_type=''

        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This field is required.")

        # add account_type
        # expect 'password mismatch' message
        username= 'wdkim'
        email = 'test@email.com'
        password='test'
        confirm_password='testtttt'
        account_type='Buyer'

        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Passwords do not match")


        # Make short passwords
        # expect 'password short' message
        username= 'wdkim'
        email = 'test@email.com'
        password='test'
        confirm_password='test'
        account_type = 'Buyer'
        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, "This field is required.")
        self.assertContains(response, "Password length must be at least 6 characters")

        

        # change password to be longer than 6 characters
        # expect 'username taken' message
        username= 'wdkim'
        email = 'test@email.com'
        password='testtest'
        confirm_password='testtest'
        account_type = 'Buyer'
        response = self.client.post(reverse('register'), {'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password, 'account_type': account_type}, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Username already taken. Please chose a different one.")



# Global aux function to avoid code duplication for templates testing
def logged_in_index_template(self, response, username):
    self.assertContains(response, username)
    self.assertContains(response, "logout")


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
        response = self.client.get(reverse('browse_listings'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "logout")
        self.assertContains(response, "No Listings are available.")

    def test_browse_listings_template_no_login(self):
        response = self.client.get(reverse('browse_listings'))
        self.assertEqual(response.status_code, 302)

    def test_browse_listings_template_logged_in(self):
        self.assertTrue(self.client.login(username='testuser', password='testuser'))
        response = self.client.get(reverse('browse_listings'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "logout")
        self.assertContains(response, "No Listings are available.")

    def test_browse_product_requests_template_no_login(self):
        response = self.client.get(reverse('browse_product_requests'))
        self.assertEqual(response.status_code, 302)

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

        

