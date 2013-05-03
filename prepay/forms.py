from django import forms
from django.contrib.auth.models import User
from prepay.models import UserProfile, PhoneNumber, WebSite, StreetAddress, InstantMessenger, Order, Review
from django.forms import ModelForm
from django.contrib.contenttypes.generic import generic_inlineformset_factory 
from prepay import settings

class CheckoutForm(forms.Form):
	quantity = forms.IntegerField(min_value=1)

class LoginForm(forms.Form):
	username=forms.CharField(max_length=15)
	password=forms.CharField(max_length=15,widget=forms.PasswordInput)


# Form for user registration. Checks to see both passwords match and len > 6
class RegistrationForm(forms.Form):
	username = forms.CharField(max_length=15)
	email = forms.EmailField(max_length=70)
	password  = forms.CharField(max_length=15,widget=forms.PasswordInput)
	confirm_password  = forms.CharField(max_length=15,widget=forms.PasswordInput)
	account_type = forms.ChoiceField(choices=(('Buyer','Buyer'), ('Seller','Seller')))

	def clean(self):
		password1 = self.cleaned_data.get('password')
		password2 = self.cleaned_data.get('confirm_password')

		if password1 and password2:
			if password1 != password2:
				raise forms.ValidationError("Passwords don't match")
			elif len(password1) < 6:
				raise forms.ValidationError("Password length must be at least 6 characters")
		return self.cleaned_data

class ListingCommentForm(forms.Form):
	comment = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'rows':'10', 'cols': '100'}))
	rating = forms.ChoiceField(
		choices=[(x,x) for x in range(0,6)]
	)
	image = forms.FileField(required=False)
	def clean(self):
		image = self.cleaned_data['image']
		if image:
			file_type = image.content_type.split('/')[0]
			if (file_type not in settings.TASK_UPLOAD_FILE_TYPES):
				raise forms.ValidationError('File type is not supported')
		return image

class ReviewForm(forms.Form):
	review = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'rows':'10', 'cols': '100'}))
	rating = forms.ChoiceField(
		choices=[(x,x) for x in range(0,6)]
	)
	
# For editing profile information
class EditProfileForm(ModelForm):
	class Meta:
		model = UserProfile
		exclude = ('username', 'password', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'groups', 'user_permissions', 'user', 'confirmation_code')

class SearchForm(forms.Form):
	q = forms.CharField(label = 'Search', max_length=30)


PhoneNumberFormSet = generic_inlineformset_factory(PhoneNumber, extra=1)
InstantMessengerFormSet = generic_inlineformset_factory(InstantMessenger, extra=1)
WebSiteFormSet = generic_inlineformset_factory(WebSite, extra=1)
StreetAddressFormSet = generic_inlineformset_factory(StreetAddress, extra=1)
