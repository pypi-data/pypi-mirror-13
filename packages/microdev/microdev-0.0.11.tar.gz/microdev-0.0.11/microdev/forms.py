from django import forms
from django.utils.translation import gettext as _


"""--------------------------------------------------------------------------
    A trivial Form to handle simple checkbox confirmation pages. DRY, right?
--------------------------------------------------------------------------"""
class ConfirmCheckboxForm(forms.Form):
    confirm = forms.BooleanField(required=True, label=_('Confirm'))


"""--------------------------------------------------------------------------
    A trivial Form to handle simple email entry pages. DRY, right?
--------------------------------------------------------------------------"""
class EmailForm(forms.Form):
	email = forms.EmailField(required=True)


"""--------------------------------------------------------------------------
    A trivial Form to handle simple File upload pages. DRY, right?
--------------------------------------------------------------------------"""
class FileForm(forms.Form):
	file = forms.FileField(required=True)


"""--------------------------------------------------------------------------
    A trivial Form to handle simple password entry pages. DRY, right?
--------------------------------------------------------------------------"""
class PasswordForm(forms.Form):
	password = forms.CharField(widget=forms.PasswordInput(), required=True)
	verify_password = forms.CharField(widget=forms.PasswordInput(), required=True)

	def clean(self):
		cleaned_data = super(PasswordForm, self).clean()
		password = cleaned_data.get("password")
		verify_password = cleaned_data.get("verify_password")

		if password != verify_password:
			raise forms.ValidationError(_("Verify password did not match."))

		# Always return the full collection of cleaned data.
		return cleaned_data



class ContactUsForm(forms.Form):
	"""
		Simple Contact Us form using a ReCaptchaField

		pip install django-recaptcha 
	"""
	from captcha.fields import ReCaptchaField
	name = forms.CharField(max_length="64", required=False)
	email = forms.EmailField(required=True)
	message = forms.CharField(widget=forms.Textarea, required=True)
	captcha = ReCaptchaField(attrs={'theme' : 'white'})

