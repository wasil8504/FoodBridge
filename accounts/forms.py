from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class DonorSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    phone_number = forms.CharField(max_length=15, required=False, help_text='Optional.')
    address = forms.CharField(widget=forms.Textarea, required=False, help_text='Optional.')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'donor'
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']
        if commit:
            user.save()
        return user


class RecipientSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    phone_number = forms.CharField(max_length=15, required=False, help_text='Optional.')
    address = forms.CharField(widget=forms.Textarea, required=False, help_text='Optional.')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'recipient'
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username or Email', max_length=255)