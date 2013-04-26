from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User, UserManager #######Jennifer
from django.db.models import permalink
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.generic import GenericRelation
from django.utils.translation import ugettext as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name    

class ProductRequest(models.Model):
    name = models.CharField(max_length=200)
    categories = models.ManyToManyField(Category)
    description = models.TextField(max_length=1000)

    def __unicode__(self):
        return self.name

class BankAccount(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User) 
    
    #might be a better way:
    #http://stackoverflow.com/questions/2013835/django-how-should-i-store-a-money-value
    balance = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __unicode__(self):
        return self.name
    

#Lara start1
class UserProfile    (User): ####Jennifer
    middle_name = models.CharField(_('middle name'), max_length=200, blank=True, null=True)
    suffix = models.CharField(_('suffix'), max_length=50, blank=True, null=True)
    nickname = models.CharField(_('nickname'), max_length=100, blank=True)
    #slug = models.SlugField(_('slug'), max_length=50, unique=True)
    slug = models.SlugField(_('slug'), max_length=50, blank=True, null=True)
    title = models.CharField(_('title'), max_length=200, blank=True)
    about = models.TextField(_('about'), blank=True)
    photo = models.ImageField(_('photo'), upload_to='%Y/%m/%d', blank=True)

    user = models.OneToOneField(User)

    phone_number = GenericRelation('PhoneNumber')

    instant_messenger = GenericRelation('InstantMessenger')
    web_site = GenericRelation('WebSite')
    street_address = GenericRelation('StreetAddress')

    class Meta:
        db_table = 'prepay_contacts_people'
        ordering = ('last_name', 'first_name')
        verbose_name = _('person')
        verbose_name_plural = _('people')

    def __str__(self):  
          return self.username

    def get_account_type(self):
        return

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

    def get_picture_url(self):
        return str(self.photo.url) 

class Seller(UserProfile):
    objects = UserManager()
    CHOICES = [(i,i) for i in range(6)]
    rating = models.IntegerField(choices=CHOICES, null=True, blank=True) 

    class Meta:
        db_table = 'prepay_contacts_sellers'
        verbose_name = 'seller'
        verbose_name_plural = 'sellers'

    def get_account_type(self):
        return str('seller')


class Buyer(UserProfile):
    objects = UserManager()
    CHOICES = [(i,i) for i in range(6)]
    rating = models.IntegerField(choices=CHOICES, null=True, blank=True) 
    class Meta:
        db_table = 'prepay_contacts_buyers'
        verbose_name = 'buyer'
        verbose_name_plural = 'buyers'

    def get_account_type(self):
        return str('buyer')

class Product(models.Model):
    name = models.CharField(max_length=200)
    seller = models.ForeignKey(Seller)
    picture = models.ImageField(upload_to='%Y/%m/%d')
    categories = models.ManyToManyField(Category)
    description = models.TextField(max_length=1000)

    def purchase(self):
        return str("sold!")

    def get_picture_url(self):
        return str(self.picture.url)

    def __unicode__(self):
        return self.name
        
class Listing(models.Model):
    name = models.CharField(max_length=50)
    CHOICES = (('Open for bidding', 'Open for bidding'),('Maximum reached', 'Maximum reached'), ('In Production', 'In Production'), ('Closed', 'Closed'), ('Aborted', 'Aborted'), ('Withdrawn', 'Withdrawn'))
    status = models.CharField(max_length=30, choices=CHOICES, default = 'Open for bidding') 
    price = models.DecimalField(max_digits=8, decimal_places=2)
    numBidders = models.IntegerField(default = 0)
    minGoal = models.IntegerField()
    maxGoal = models.IntegerField()
    deadlineBid = models.DateTimeField()
    deadlineDeliver = models.DateTimeField()
    product = models.ForeignKey(Product)
    description = models.TextField(max_length=1000)

    
    created_at = models.DateTimeField(auto_now_add=True)
    date_closed = models.DateTimeField(_('date closed'),null=True, blank=True)
    date_withdrawn = models.DateTimeField(_('date withdrawn'),null=True, blank=True)
    date_aborted = models.DateTimeField(_('date aborted'),null=True, blank=True)
    
    def offer(self):
        return str("offered!")
    
    def withdraw(self):
        return str("withdrawn!")
    
    def __unicode__(self):
        return self.name

class Listing_Comment(models.Model):
	listing = models.ForeignKey(Listing)
	commenter=models.ForeignKey(UserProfile)
	comment = models.CharField(max_length=1000)
	rating = models.IntegerField(
		default=1,
		validators=[
			MaxValueValidator(5),
			MinValueValidator(0)
		]
	)
	date = models.DateTimeField('Date added')
	image = models.ImageField(_('image'), upload_to='listing/comment/img',null=True, blank=True)
	def __unicode__(self):
		return u'%s %d' % (self.comment, self.rating)
	class Meta:
		db_table = 'prepay_listins_comments'
		verbose_name = 'listing comment'
		verbose_name_plural = 'listing comments'

class Bank(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name
    
class Escrow(models.Model):
    name = models.CharField(max_length=50)
    listing = models.ForeignKey(Listing)
    balance = models.DecimalField(max_digits=8, decimal_places=2)
    def __unicode__(self):
        return self.name

class Order(models.Model):
    CHOICES = (('Ongoing', 'Ongoing'), ('Closed', 'Closed'), ('Aborted by seller', 'Aborted by seller'), ('Rated', 'Rated'), ('Withdrawn', 'Withdrawn'))
    status = models.CharField(max_length=30, choices=CHOICES, default = 'Ongoing') 
    buyer = models.ForeignKey(Buyer)
    seller = models.ForeignKey(Seller)
    listing = models.ForeignKey(Listing)
    date_added = models.DateTimeField(_('date added'), auto_now_add=True)
    date_delivered = models.DateTimeField(_('date delivered'),null=True, blank=True)
    date_withdrawn = models.DateTimeField(_('date withdrawn'),null=True, blank=True)
    date_aborted= models.DateTimeField(_('date aborted'),null=True, blank=True)
    shipping_address = GenericRelation('StreetAddress')

    def __unicode__(self):
        return self.listing.name

    class Meta:
        ordering = ["-date_added"]

class Review(models.Model):
    order = models.ForeignKey(Order)
    seller = models.ForeignKey(Seller)
    buyer = models.ForeignKey(Buyer)
    review = models.CharField(max_length=1000)
    rating = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ]
    )
    date_added = models.DateTimeField(_('date added'), auto_now_add=True)
    def __unicode__(self):
        return u'%s %d' % (self.review, self.rating)

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

def save_escrow_handler(sender, **kwargs):
	l = kwargs['instance']
	if kwargs['created']:
		l.escrow_set.create(name=l.name, listing = l, balance = 0)
	return

post_save.connect(save_escrow_handler, sender = Listing)

