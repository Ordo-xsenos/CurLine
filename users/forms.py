from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
#from .models import User, Profile
from django.contrib.auth import get_user_model

User = get_user_model()  # Берём кастомную модель пользователя

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input', 'placeholder': 'username', 'autocomplete': 'username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input', 'placeholder': 'password', 'autocomplete': 'current-password'
    }))

    class Meta:
        model = User
        fields = ('username', 'password')

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'contact__section-input', 'placeholder': 'username'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'contact__section-input', 'placeholder': 'email', 'autocomplete': 'email'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input', 'placeholder': 'password', 'autocomplete': 'new-password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'contact__section-input', 'placeholder': 'confirm password', 'autocomplete': 'new-password'
    }))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2


class UserEditForm(UserChangeForm):
    #first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'contact__section-input'}))
    #last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'contact__section-input'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'contact__section-input'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'contact__section-input'}))

    class Meta:
        model = User
        fields = ('username', 'email')
