from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User, UserManager #######Jennifer

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name    
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    #seller = models.ForeignKey(Seller)
    picture = models.ImageField(upload_to='%Y/%m/%d')
    categories = models.ManyToManyField(Category)
    description = models.TextField(max_length=1000)

    def purchase(self):
        return str("sold!")

    def get_picture_url(self):
        return str(self.picture.url)

    def __unicode__(self):
        return self.name

class BankAccount(models.Model):
    name = models.CharField(max_length=50)
    
    #might be a better way:
    #http://stackoverflow.com/questions/2013835/django-how-should-i-store-a-money-value
    balance = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __unicode__(self):
        return self.name
    


'''
class PrePayUser(User, models.Model):

    bank_account = models.ForeignKey(BankAccount)
    name = models.CharField(max_length=60)
    
    def __unicode__(self):
        return self.name
'''
#Lara start1
class UserProfile    (models.Model):
	first_name = models.CharField(_('first name'), max_length=100)
	last_name = models.CharField(_('last name'), max_length=200)
	middle_name = models.CharField(_('middle name'), max_length=200, blank=True, null=True)
	suffix = models.CharField(_('suffix'), max_length=50, blank=True, null=True)
	nickname = models.CharField(_('nickname'), max_length=100, blank=True)
	slug = models.SlugField(_('slug'), max_length=50, unique=True)
	title = models.CharField(_('title'), max_length=200, blank=True)
	about = models.TextField(_('about'), blank=True)
	photo = models.ImageField(_('photo'), upload_to='contacts/person/', blank=True)

	user = models.OneToOneField(User)
	
	phone_number = GenericRelation('PhoneNumber')
	email_address = GenericRelation('EmailAddress')
	instant_messenger = GenericRelation('InstantMessenger')
	web_site = GenericRelation('WebSite')
	street_address = GenericRelation('StreetAddress')

	date_added = models.DateTimeField(_('date added'), auto_now_add=True)
	date_modified = models.DateTimeField(_('date modified'), auto_now=True)
	
	class Meta:
		db_table = 'prepay_contacts_people'
		ordering = ('last_name', 'first_name')
		verbose_name = _('person')
		verbose_name_plural = _('people')

	def __str__(self):  
          return self.fullname
	def fullname(self):
		return u"%s %s" % (self.first_name, self.last_name)

	@permalink
	def get_absolute_url(self):
		return ('contacts_person_detail', None, {
		'pk': self.pk,
		'slug': self.slug,
	})

	@permalink
	def get_update_url(self):
		return ('contacts_person_update', None, {
		'pk': self.pk,
		'slug': self.slug,
	})

	@permalink
	def get_delete_url(self):
		return ('contacts_person_delete', None, {
		'pk': self.pk,
		'slug': self.slug,
	})

class Seller(models.Model):
	account = models.OneToOneField(UserProfile)   #####Jennifer
	products = models.ManyToManyField(Product) #todo: filter by owner
	#products = product_set.all()
	#bank_account = models.ForeignKey(BankAccount)
	#we might want to check out https://github.com/dcramer/django-ratings
	CHOICES = [(i,i) for i in range(6)]
	rating = models.IntegerField(choices=CHOICES, null=True, blank=True) 
###Jennifer edited
	class Meta:
		db_table = 'prepay_contacts_sellers'
		verbose_name = 'seller'
		verbose_name_plural = 'sellers'

#####Jennifer from here
class Buyer(models.Model):
	account = models.OneToOneField(UserProfile)
	CHOICES = [(i,i) for i in range(6)]
	rating = models.IntegerField(choices=CHOICES, null=True, blank=True) 
	class Meta:
		db_table = 'prepay_contacts_buyers'
		verbose_name = 'buyer'
		verbose_name_plural = 'buyers'
#Lara end1

class Listing(models.Model):
    name = models.CharField(max_length=50)
    seller = models.ForeignKey(Seller)
    product = models.ForeignKey(Product)
    description = models.TextField(max_length=1000)
    #quantity = models.IntegerField()
    #price_per = CurrencyField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def offer(self):
        return str("offered!")
    
    def withdraw(self):
        return str("withdrawn!")
    
    def __unicode__(self):
        return self.name
    
class Bank(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name
    
class Escrow(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name


#Lara start2
PHONE_LOCATION_CHOICES = (
	('work', _('Work')),
	('mobile', _('Mobile')),
	('fax', _('Fax')),
	('pager', _('Pager')),
	('home', _('Home')),
	('other', _('Other')),
)

class PhoneNumber(models.Model):
	"""Phone Number model."""
	content_type = models.ForeignKey(ContentType,
	limit_choices_to={'app_label': 'prepay'})
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()

	phone_number = models.CharField(_('number'), max_length=50)
	location = models.CharField(_('location'), max_length=6,
	choices=PHONE_LOCATION_CHOICES, default='work')

	date_added = models.DateTimeField(_('date added'), auto_now_add=True)
	date_modified = models.DateTimeField(_('date modified'), auto_now=True)

	def __unicode__(self):
		return u"%s (%s)" % (self.phone_number, self.location)

	class Meta:
		db_table = 'prepay_contacts_phone_numbers'
		verbose_name = 'phone number'
		verbose_name_plural = 'phone numbers'

LOCATION_CHOICES = (
	('work', _('Work')),
	('home', _('Home')),
	('mobile', _('Mobile')),
	('fax', _('Fax')),
	('person', _('Personal')),
	('other', _('Other'))
)

class EmailAddress(models.Model):
	content_type = models.ForeignKey(ContentType,	limit_choices_to={'app_label': 'prepay'})
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()

	email_address = models.EmailField(_('email address'))
	location = models.CharField(_('location'), max_length=6,
	choices=LOCATION_CHOICES, default='work')

	date_added = models.DateTimeField(_('date added'), auto_now_add=True)
	date_modified = models.DateTimeField(_('date modified'), auto_now=True)

	def __unicode__(self):
		return u"%s (%s)" % (self.email_address, self.location)

	class Meta:
		db_table = 'prepay_contacts_email_addresses'
		verbose_name = 'email address'
		verbose_name_plural = 'email addresses'



IM_SERVICE_CHOICES = (
('aim', 'AIM'),
('msn', 'MSN'),
('icq', 'ICQ'),
('jabber', 'Jabber'),
('yahoo', 'Yahoo'),
('skype', 'Skype'),
('qq', 'QQ'),
('sametime', 'Sametime'),
('gadu-gadu', 'Gadu-Gadu'),
('google-talk', 'Google Talk'),
('twitter', 'Twitter'),
('other', _('Other'))
)

class InstantMessenger(models.Model):
	content_type = models.ForeignKey(ContentType,
	limit_choices_to={'app_label': 'prepay'})
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()

	im_account = models.CharField(_('im account'), max_length=100)
	location = models.CharField(_('location'), max_length=6,
	choices=LOCATION_CHOICES, default='work')
	service = models.CharField(_('service'), max_length=11,
	choices=IM_SERVICE_CHOICES, default='jabber')

	date_added = models.DateTimeField(_('date added'), auto_now_add=True)
	date_modified = models.DateTimeField(_('date modified'), auto_now=True)

	def __unicode__(self):
		return u"%s (%s)" % (self.im_account, self.location)

	class Meta:
		db_table = 'prepay_contacts_instant_messengers'
		verbose_name = 'instant messenger'
		verbose_name_plural = 'instant messengers'


class WebSite(models.Model):
	content_type = models.ForeignKey(ContentType,
	limit_choices_to={'app_label': 'prepay'})
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()

	url = models.URLField(_('URL'))
	location = models.CharField(_('location'), max_length=6,
	choices=LOCATION_CHOICES, default='work')

	date_added = models.DateTimeField(_('date added'), auto_now_add=True)
	date_modified = models.DateTimeField(_('date modified'), auto_now=True)

	def __unicode__(self):
		return u"%s (%s)" % (self.url, self.location)

	class Meta:
		db_table = 'prepay_contacts_web_sites'
		verbose_name = _('web site')
		verbose_name_plural = _('web sites')

	def get_absolute_url(self):
		return u"%s?web_site=%s" % (self.content_object.get_absolute_url(), self.pk)


class StreetAddress(models.Model):
	content_type = models.ForeignKey(ContentType,
	limit_choices_to={'app_label': 'prepay'})
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()

	street = models.TextField(_('street'), blank=True)
	city = models.CharField(_('city'), max_length=200, blank=True)
	province = models.CharField(_('province'), max_length=200, blank=True)
	postal_code = models.CharField(_('postal code'), max_length=10, blank=True)
	country = models.CharField(_('country'), max_length=100)
	location = models.CharField(_('location'), max_length=6,
	choices=LOCATION_CHOICES, default='work')

	date_added = models.DateTimeField(_('date added'), auto_now_add=True)
	date_modified = models.DateTimeField(_('date modified'), auto_now=True)

	def __unicode__(self):
		return u"%s (%s)" % (self.city, self.location)

	class Meta:
		db_table = 'prepay_contacts_street_addresses'
		verbose_name = _('street address')
		verbose_name_plural = _('street addresses')
#Lara end2

#editted by Lara, reference: https://github.com/myles/django-contacts/blob/master/src/contacts/models.py

class Listing(models.Model):
    name = models.CharField(max_length=50)
    seller = models.ForeignKey(Seller)
    product = models.ForeignKey(Product)
    description = models.TextField(max_length=1000)
    #quantity = models.IntegerField()
    #price_per = CurrencyField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def offer(self):
        return str("offered!")
    
    def withdraw(self):
        return str("withdrawn!")
    
    def __unicode__(self):
        return self.name
    
class Bank(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name
    
class Escrow(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name

