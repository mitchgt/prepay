from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User, UserManager #######Jennifer

'''
#http://stackoverflow.com/questions/2013835/django-how-should-i-store-a-money-value
class CurrencyField(models.DecimalField):
  __metaclass__ = models.SubfieldBase

  def __init__(self, verbose_name=None, name=None, **kwargs):
    super(CurrencyField, self). __init__(
        verbose_name=verbose_name, name=name, max_digits=10,
        decimal_places=2, **kwargs)

  def to_python(self, value):
    try:
      return super(CurrencyField, self).to_python(value).quantize(Decimal("0.01"))
    except AttributeError:
      return None
'''

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

'''
I'm implementing these user classes, possibly just for version 0
convenience.  We need to reconcile this with using the Admin site
for users, roles, permissions, etc.
'''
#####Jennifer deleted custom user

class Seller(User):
    account = models.OneToOneField(User)   #####Jennifer 
    objects = UserManager() ###Jennifer
    products = models.ManyToManyField(Product) #todo: filter by owner
    #products = product_set.all()
    
    #we might want to check out https://github.com/dcramer/django-ratings
    CHOICES = [(i,i) for i in range(6)]
    rating = models.IntegerField(choices=CHOICES, null=True, blank=True)  ###Jennifer edited

#####Jennifer from here
class Buyer(User):
    account = models.OneToOneField(User)
    objects = UserManager() ###Jennifer
    CHOICES = [(i,i) for i in range(6)]
    rating = models.IntegerField(choices=CHOICES, null=True, blank=True) 
#####Jennifer above

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
    
class Listing(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name
