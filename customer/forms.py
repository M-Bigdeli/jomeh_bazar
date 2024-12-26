from django import forms
from .models import Customer, Address
from django.core.exceptions import ValidationError


class CustomerRegisterForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام',
                'required': 'required',
                'data-error': 'نام',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام خانوادگی',
                'required': 'required',
                'data-error': 'نام خانوادگی',
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره تلفن',
                'required': 'required',
                'data-error': 'شماره تلفن',
                'id': 'phone_number',
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'رمزعبور',
                'required': 'required',
                'id': 'password',
            }),
        }


class CustomerLogInForm(forms.Form):
    username = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'شماره تلفن',
            'required': 'required',
            'data-error': 'شماره تلفن',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمزعبور',
            'required': 'required',
        }),
        required=True,
    )


class ForgetPasswordForm(forms.Form):
    """
    This form is for getting the phone number of a user who has forgotten their password.
    """
    username = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'شماره تلفن',
            'required': 'required',
            'data-error': 'شماره تلفن',
        })
    )


class ChangePasswordForm(forms.Form):
    """
    This form is for changing the password of a user who has forgotten their password.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور جدید',
            'required': 'required',
            'id': 'password',
        }),
        required=True,
    )


class ChangePasswordAuthenticatedUserForm(forms.Form):
    """
    This form is for changing the password of an authenticated user who wants to change their password.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور فعلی',
            'required': 'required',
        }),
        required=True,
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور جدید',
            'required': 'required',
            'id': 'password',
        }),
        required=True,
    )


class ChangeNameForm(forms.ModelForm):
    """
    This form is for changing the first and last name of an authenticated user who wants to change them.
    """
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام',
                'required': 'required',
                'data-error': 'لطفاً این فیلد را پر کنید.',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام خانوادگی',
                'required': 'required',
                'data-error': 'لطفاً این فیلد را پر کنید.',
            }),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise ValidationError("")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise ValidationError("")
        return last_name


class AddressForm(forms.ModelForm):
    """
    This form is used to add and edit user addresses.
    """
    class Meta:
        model = Address
        fields = ['state', 'city', 'address', 'postal_code']
        widgets = {
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'استان',
                'required': 'required',
                'data-error': 'لطفاً این فیلد را پر کنید.',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شهر',
                'required': 'required',
                'data-error': 'لطفاً این فیلد را پر کنید.',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'کد پستی',
                'required': 'required',
                'data-error': 'لطفاً این فیلد را پر کنید.',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'آدرس',
                'required': 'required',
                'data-error': 'لطفاً این فیلد را پر کنید.',
            }),
        }
