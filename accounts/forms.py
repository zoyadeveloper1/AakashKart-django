from django import forms
from .models import Account
from django.contrib.auth.forms import AuthenticationForm


# Registration Form
class RegistrationForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Password',
            'class': 'form-control',
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control',
        })
    )

    class Meta:
        model = Account
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'password',
            'confirm_password',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")

        return cleaned_data

    def save(self, commit=True):
        account = super().save(commit=False)

        # Password hash
        account.set_password(self.cleaned_data['password'])

        if commit:
            account.save()

        return account


# Login Form
class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Email or Username',
            'class': 'form-control',
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Password',
            'class': 'form-control',
        })
    )