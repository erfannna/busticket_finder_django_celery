from django import forms
from .models import User
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm


class UserCreationForm(BaseUserCreationForm):

    class Meta:
        model = User
        fields = ("phone_number", "email", "first_name", "last_name",
                  "is_staff", "is_active", "sub_expire_date", "subscription", "sub_type")


class UserChangeForm(BaseUserChangeForm):

    class Meta:
        model = User
        fields = ("phone_number", "email", "first_name", "last_name",
                  "is_staff", "is_active", "sub_expire_date", "subscription", "sub_type")


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': "text-input",
            'id': "password",
            'placeholder': "رمز عبور",
            'required': "true"
        }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': "text-input",
            'id': "password2",
            'placeholder': "تایید رمز عبور",
            'required': "true"
        }))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': "text-input",
                'id': "first_name",
                'maxlength': "50",
                'placeholder': "نام",
                'required': "true"
            }),
            'last_name': forms.TextInput(attrs={
                'class': "text-input",
                'id': "last_name",
                'maxlength': "50",
                'placeholder': "نام خانوادگی",
                'required': "true"
            }),
            'phone_number': forms.NumberInput(attrs={
                'class': "text-input",
                'id': "phone_number",
                'maxlength': "11",
                'placeholder': "شماره همراه",
                'pattern': "\d{11}"
            })
        }


class LoginForm(forms.Form):

    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': "text-input",
            'id': "phone_number",
            'maxlength': "11",
            'placeholder': "شماره همراه",
            'pattern': "\d{11}"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'password',
            'class': "text-input",
            'placeholder': "رمز عبور"
        }),
    )


class AccountEditForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': "formTextBox",
            'id': "password",
            'placeholder': "رمز عبور فعلی",
        }), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
            'class': "formTextBox",
            'id': "password2",
            'placeholder': "رمز عبور جدید",
        }), required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': "formTextBox",
                'id': "first_name",
                'maxlength': "50",
                'placeholder': "نام",
                'required': "true"
            }),
            'last_name': forms.TextInput(attrs={
                'class': "formTextBox",
                'id': "last_name",
                'maxlength': "50",
                'placeholder': "نام خانوادگی",
                'required': "true"
            }),
            'phone_number': forms.NumberInput(attrs={
                'class': "formTextBox",
                'id': "phone_number",
                'maxlength': "11",
                'placeholder': "شماره همراه",
                'readonly': ""
            })
        }
