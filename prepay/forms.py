from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
  username = forms.CharField(max_length=15)
	email = forms.EmailField(max_length=70)
	password  = forms.CharField(max_length=15)
	account_type = forms.ChoiceField(
		choices=(('Buyer','Buyer'), ('Seller','Seller'))
	)
