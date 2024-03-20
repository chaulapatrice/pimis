from django import forms
from users.models import User


class SignUpForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    def validate_email(self, value):
        if User.objects.exists(email=value):
            raise forms.ValidationError('Email already taken')

        return value

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class SignoutForm(forms.Form):
    signout = forms.IntegerField()