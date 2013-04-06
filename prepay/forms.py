from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
	username=forms.CharField(max_length=15)
	password=forms.CharField(max_length=15,widget=forms.PasswordInput)

class RegistrationForm(forms.Form):
	username = forms.CharField(max_length=15)
	email = forms.EmailField(max_length=70)
	password  = forms.CharField(max_length=15,widget=forms.PasswordInput)
	account_type = forms.ChoiceField(
	choices=(('Buyer','Buyer'), ('Seller','Seller')))

class ListingCommentForm(forms.Form):
	comment = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'rows':'10', 'cols': '100'}))
	rating = forms.ChoiceField(
		choices=[(x,x) for x in range(0,6)]
	)
	image = forms.FileField(required=False)
	def clean(self):
		image = self.cleaned_data['picture']
		if image:
			file_type = image.content_type.split('/')[0]
			if (file_type not in settings.TASK_UPLOAD_FILE_TYPES):
				raise forms.ValidationError('File type is not supported')
		return image
