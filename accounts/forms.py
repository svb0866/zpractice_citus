from django import forms
from .models import User
from intl_tel_input.widgets import IntlTelInputWidget
from phonenumbers import parse, is_valid_number


class TeamRegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'is_clinician',
                  'is_scheduler', 'is_biller', )
        required = ('username', 'first_name', 'last_name', 'email', 'phone')
        labels = {
            "username": "Username",
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email ID",
            "phone": "Valid Phone number",
            "is_clinician": "Clinician Role",
            "is_scheduler": "Can Schedule Appointments",
            "is_biller": "Can Manage Billing",
        }
        widgets = {
            'phone': IntlTelInputWidget(default_code='us')
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError("Username is taken")
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        qs = User.objects.filter(phone=phone)
        if qs.exists():
            raise forms.ValidationError("Phone Number is already registered")
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


class TeamMemberUpdateForm(forms.Form):
    is_clinician = forms.BooleanField(initial=True, required=False)
    is_scheduler = forms.BooleanField(initial=True, required=False)
    is_biller = forms.BooleanField(initial=False, required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone = forms.CharField(widget=IntlTelInputWidget(default_code='us'))
    email = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user_obj')  # cache the user object you pass in
        super(TeamMemberUpdateForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs:
            if self.user != qs.first():
                raise forms.ValidationError("email is taken")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if qs:
            if self.user != qs.first():
                raise forms.ValidationError("Username is taken")
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        qs = User.objects.filter(phone=phone)
        if qs.exists():
            if self.user != qs.first():
                raise forms.ValidationError("Phone Number is already registered")
        ph = parse(phone)
        if not is_valid_number(ph):
            raise forms.ValidationError("Phone Number is Invalid")
        return phone