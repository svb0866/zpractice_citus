from django import forms
from customers.models import Customer
from intl_tel_input.widgets import IntlTelInputWidget


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput, required=True)

    class Meta:
        model = Customer
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'timezone')
        labels = {
            "username": "Username",
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email ID",
            "phone": "Valid Phone number",
        }
        widgets = {
            'phone': IntlTelInputWidget(default_code='us')
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Customer.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = Customer.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError("Username is taken")
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        qs = Customer.objects.filter(phone=phone)
        if qs.exists():
            raise forms.ValidationError("Phone Number is already registered")
        from phonenumbers import parse, is_valid_number
        ph = parse(phone)
        if not is_valid_number(ph):
            raise forms.ValidationError("Phone Number is Invalid")
        return phone

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2