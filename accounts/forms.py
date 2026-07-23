from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import CustomUser
from django.core.validators import RegexValidator


class DonorSignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text='Required. Inform a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your email address'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text='Optional.',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your phone number (optional)'
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your address (optional)'
        }),
        required=False,
        help_text='Optional.'
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required.',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required.',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your last name'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update widget attributes for password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Confirm your password'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Choose a username'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'donor'
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class RecipientSignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text='Required. Inform a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your email address'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text='Optional.',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your phone number (optional)'
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your address (optional)'
        }),
        required=False,
        help_text='Optional.'
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required.',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required.',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your last name'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update widget attributes for password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Confirm your password'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Choose a username'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'recipient'
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or Email',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent mb-4',
            'placeholder': 'Enter your username or email'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'placeholder': 'Enter your password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the widget for better UX
        self.fields['username'].widget.attrs.update({
            'autocomplete': 'username'
        })
        self.fields['password'].widget.attrs.update({
            'autocomplete': 'current-password'
        })