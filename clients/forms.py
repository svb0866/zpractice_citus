from django import forms
from clients.models import ClientNote, ClientAdministrativeNote, Client, EmailTemplates, ClientFile
from intl_tel_input.widgets import IntlTelInputWidget
from phonenumbers import parse, is_valid_number


class ClientAdministrativeNoteForm(forms.ModelForm):
    class Meta:
        model = ClientAdministrativeNote
        fields = ['administrative_note_body', ]


class ClientNoteForm(forms.ModelForm):
    class Meta:
        model = ClientNote
        fields = ['client_note_title', 'client_note_body']


class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ('uuid', 'created_datetime', 'created_by', 'last_modified', 'last_modified_by')
        widgets = {
            'phone1': IntlTelInputWidget(default_code='us'),
            'phone2': IntlTelInputWidget(default_code='us'),
            'phone3': IntlTelInputWidget(default_code='us'),
            'emergency_phone': IntlTelInputWidget(default_code='us'),
            'insured_phone': IntlTelInputWidget(default_code='us'),
        }

    def clean_primary_email(self):
        primary_email = self.cleaned_data.get('primary_email')
        qs = Client.objects.filter(primary_email=primary_email)
        qs_exists = qs.first()
        if qs_exists is not None:
            if self.instance != qs_exists:
                raise forms.ValidationError("This primary email belongs to {} {} {}".format(
                    qs_exists.first_name, qs_exists.last_name, qs_exists.primary_email))
        return primary_email

    def clean_phone1(self):
        phone1 = self.cleaned_data.get('phone1')
        qs = Client.objects.filter(phone1=phone1)
        qs_exists = qs.first()
        if qs_exists is not None:
            if self.instance != qs_exists:
                raise forms.ValidationError("Primary Phone number already Registered by {} {} {}".format(
                    qs_exists.first_name, qs_exists.last_name, qs_exists.primary_email))
        ph = parse(phone1)
        if not is_valid_number(ph):
            raise forms.ValidationError("Phone Number is Invalid")
        return phone1

    def clean_phone2(self):
        phone2 = self.cleaned_data.get('phone2')
        if phone2 is not None:
            ph = parse(phone2)
            if not is_valid_number(ph):
                raise forms.ValidationError("Phone Number is Invalid")
        return phone2

    def clean_phone3(self):
        phone3 = self.cleaned_data.get('phone3')
        if phone3 is not None:
            ph = parse(phone3)
            if not is_valid_number(ph):
                raise forms.ValidationError("Phone Number is Invalid")
        return phone3

    def clean_insured_phone(self):
        insured_phone = self.cleaned_data.get('insured_phone')
        if insured_phone is not None:
            ph = parse(insured_phone)
            if not is_valid_number(ph):
                raise forms.ValidationError("Phone Number is Invalid")
        return insured_phone

    def clean_emergency_phone(self):
        emergency_phone = self.cleaned_data.get('emergency_phone')
        if emergency_phone is not None:
            ph = parse(emergency_phone)
            if not is_valid_number(ph):
                raise forms.ValidationError("Phone Number is Invalid")
        return emergency_phone


class ClientEmailTemplateUpdateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplates
        fields = ['email_reminder_setting', 'appointment_reminder', 'new_appointment', 'appointment_reschedule',
                  'appointment_canceled', 'client_onboarding']


class ClientFileUploadForm(forms.ModelForm):
    class Meta:
        model = ClientFile
        fields = ['file']

    def clean_file(self):
        # 2.5MB - 2621440
        # 5MB - 5242880
        # 10MB - 10485760
        # 20MB - 20971520
        # 50MB - 5242880
        # 100MB 104857600
        # 250MB - 214958080
        # 500MB - 429916160
        file = self.cleaned_data['file']
        if file.size > 20971520:
            raise forms.ValidationError('Please keep file size under 20 Mb. Current file size of the upload is {} Mb'.format(round(file.size/1000000)))

        return file


class ClientCreateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'phone1', 'phone2', 'phone3',
                  'primary_email', 'secondary_email', 'billing_type', 'referred_by', 'client_minor',
                  'send_email_appointment_reminders', 'access_client_portal')
        required = ('first_name', 'email')

        widgets = {
            'phone1': IntlTelInputWidget(default_code='us'),
            'phone2': IntlTelInputWidget(default_code='us'),
            'phone3': IntlTelInputWidget(default_code='us'),
        }

    def clean_primary_email(self):
        primary_email = self.cleaned_data.get('primary_email')
        qs = Client.objects.filter(primary_email=primary_email)
        qs_exists = qs.first()
        if qs_exists is not None:
            raise forms.ValidationError("This primary email belongs to {} {} {}".format(
                qs_exists.first_name, qs_exists.last_name, qs_exists.primary_email))
        return primary_email

    def clean_phone1(self):
        print(self.cleaned_data.get('phone1'), 'opop')
        phone1 = self.cleaned_data.get('phone1')
        qs = Client.objects.filter(phone1=phone1)
        qs_exists = qs.first()
        if qs_exists is not None:
            raise forms.ValidationError("Primary Phone number already Registered by {} {} {}".format(
                qs_exists.first_name, qs_exists.last_name, qs_exists.primary_email))
        ph = parse(phone1)
        if not is_valid_number(ph):
            raise forms.ValidationError("Phone Number is Invalid")
        return phone1

    def clean_phone2(self):
        phone2 = self.cleaned_data.get('phone2')
        ph = parse(phone2)
        if not is_valid_number(ph):
            raise forms.ValidationError("Phone Number is Invalid")
        return phone2

    def clean_phone3(self):
        phone3 = self.cleaned_data.get('phone3')
        ph = parse(phone3)
        if not is_valid_number(ph):
            raise forms.ValidationError("Phone Number is Invalid")
        return phone3
