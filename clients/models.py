import os

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import models
import uuid
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone
from guardian.models import UserObjectPermissionBase
from guardian.models import GroupObjectPermissionBase
from ckeditor.fields import RichTextField
from django.shortcuts import reverse
from guardian.shortcuts import assign_perm

from accounts.models import User, UserManager
from phonenumbers import parse, format_number, PhoneNumberFormat
from django_clamd.validators import validate_file_infection
from clients import emailer
from customers.models import ActivityStream, Customer
from django.conf import settings
from django_multitenant.fields import *
from django_multitenant.models import *


class Client(TenantModel):
    BILLING_TYPE_CHOICES = [
        ('self', 'Self Pay'),
        ('insurance', 'Insurance'),
    ]

    PHONE_CHOICES = [
        ('work', 'Work'),
        ('mobile', 'Mobile'),
        ('home', 'Home'),
        ('fax', 'Fax'),
    ]

    EMAIL_CHOICES = [
        ('work', 'Work'),
        ('home', 'Home'),
    ]

    ''' Permissions for guardian related'''
    PERMISSIONS = (
        ('can_view', 'Can View'),
        ('can_edit', 'Can Edit'),
        ('can_delete', 'Can Delete'),
        ('can_add', 'Can Add'),
        ('can_notes', 'Can View Notes'),
    )

    CAN_VIEW = PERMISSIONS[0][0]
    CAN_EDIT = PERMISSIONS[1][0]
    CAN_DELETE = PERMISSIONS[2][0]
    CAN_ADD = PERMISSIONS[3][0]
    CAN_NOTES = PERMISSIONS[4][0]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    tenant_id = 'customer_id'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    client_user_obj = TenantForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    suffix = models.CharField(max_length=10, null=True, blank=True)
    preferred_name = models.CharField(max_length=50, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    client_minor = models.BooleanField(default=False, blank=True)
    send_text_appointment_reminders = models.BooleanField(default=False, blank=True)
    send_email_appointment_reminders = models.BooleanField(default=False, blank=True)
    billing_type = models.CharField(max_length=15, choices=BILLING_TYPE_CHOICES,
                                    default=BILLING_TYPE_CHOICES[0][0], blank=True)
    referred_by = models.CharField(max_length=50, null=True, blank=True)

    phone1 = models.CharField(max_length=20, null=True, blank=True)
    text_message_consent_1 = models.BooleanField(default=False, blank=True)

    phone2 = models.CharField(max_length=20, null=True, blank=True)
    text_message_consent_2 = models.BooleanField(default=False, blank=True)

    phone3 = models.CharField(max_length=20, null=True, blank=True)
    text_message_consent_3 = models.BooleanField(default=False, blank=True)

    primary_email = models.EmailField(max_length=50, unique=True)
    primary_email_consent = models.BooleanField(default=False, blank=True)

    secondary_email = models.EmailField(max_length=50, null=True, blank=True)
    secondary_email_consent = models.BooleanField(default=False, blank=True)

    access_client_portal = models.BooleanField(default=True, blank=True)
    '''Address'''
    sex = models.CharField(max_length=20, null=True, blank=True)
    relationship_status = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip = models.CharField(max_length=6, null=True, blank=True)

    '''Emergency'''
    emergency_first_name = models.CharField(max_length=50, null=True, blank=True)
    emergency_last_name = models.CharField(max_length=50, null=True, blank=True)
    emergency_relation = models.CharField(max_length=20, null=True, blank=True)
    emergency_phone = models.CharField(max_length=20, null=True, blank=True)
    emergency_email = models.CharField(max_length=50, null=True, blank=True)
    emergency_phone_type = models.CharField(max_length=20, null=True, blank=True)
    '''Insurance'''
    insurance_company = models.CharField(max_length=50, null=True, blank=True)
    group_id = models.CharField(max_length=50, null=True, blank=True)
    plan_id = models.CharField(max_length=50, null=True, blank=True)
    member_id = models.CharField(max_length=50, null=True, blank=True)
    client_relationship_to_insured = models.CharField(max_length=50, null=True, blank=True)
    insured_first_name = models.CharField(max_length=50, null=True, blank=True)
    insured_last_name = models.CharField(max_length=50, null=True, blank=True)
    insured_sex = models.CharField(max_length=20, null=True, blank=True)
    insured_birth_date = models.CharField(max_length=50, null=True, blank=True)
    insured_phone = models.CharField(max_length=50, null=True, blank=True)
    insured_address = models.CharField(max_length=500, null=True, blank=True)
    insured_city = models.CharField(max_length=50, null=True, blank=True)
    insured_state = models.CharField(max_length=50, null=True, blank=True)
    insured_zip = models.CharField(max_length=6, null=True, blank=True)

    created_datetime = models.DateTimeField(auto_now=False, default=timezone.now)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now_add=False, default=timezone.now)
    last_modified_by = models.CharField(max_length=50, blank=True, null=True)

    class Meta(object):
        permissions = (
            ('can_view', 'Can View'),
            ('can_edit', 'Can Edit'),
            ('can_add', 'Can Add'),
            ('can_delete', 'Can Add'),
            ('can_notes', 'Can View Notes'),
        )
        unique_together = ["id", "customer"]

    def __str__(self):
        fullname = ""
        if self.first_name:
            fullname = fullname+self.first_name+" "
        if self.middle_name:
            fullname = fullname+self.middle_name+" "
        if self.last_name:
            fullname = fullname+self.last_name+" "
        if self.suffix:
            fullname = fullname+self.suffix+" "
        return fullname

    def get_absolute_url(self):
        return reverse('clients:client-detail', kwargs={'uuid': self.uuid})

    def get_delete_url(self):
        return reverse('clients:client-delete', kwargs={'uuid': self.uuid})

    def get_update_url(self):
        return reverse('clients:client-update', kwargs={'uuid': self.uuid})

    def get_set_appointment_url(self):
        return reverse('appointments:appointment-create', kwargs={'uuid': self.uuid})

    def get_appointment_list_url(self):
        return reverse('clients:client-appointments', kwargs={'uuid': self.uuid})

    def get_portal_toggle_url(self):
        return reverse('clients:client-portal-access', kwargs={'uuid': self.uuid})

    def get_upcoming_appointments(self):
        return self.appointment_set.filter(appointment_datetime_utc__gte=timezone.now())

    def get_parsed_phone1(self):
        if self.phone1 is not None:
            ph = parse(self.phone1)
            return format_number(ph, PhoneNumberFormat.INTERNATIONAL)
        return None

    def get_parsed_phone2(self):
        if self.phone2 is not None:
            ph = parse(self.phone2)
            return format_number(ph, PhoneNumberFormat.INTERNATIONAL)
        return None

    def get_parsed_phone3(self):
        if self.phone3 is not None:
            ph = parse(self.phone3)
            return format_number(ph, PhoneNumberFormat.INTERNATIONAL)
        return None

    def get_parsed_emergency_phone(self):
        if self.emergency_phone is not None:
            ph = parse(self.emergency_phone)
            return format_number(ph, PhoneNumberFormat.INTERNATIONAL)
        return None

    def create_client_portal_credentials(self, requester: User):
        if self.client_user_obj is None:
            client_user_manager = UserManager()
            password = client_user_manager.make_random_password()
            client_user_obj = client_user_manager.create_user(
                customer=requester.customer,
                username=self.primary_email,
                first_name="un_assigned" if self.first_name is None else self.first_name,
                last_name="un_assigned" if self.first_name is None else self.first_name,
                email=self.primary_email,
                phone="un_assigned" if self.first_name is None else self.first_name,
                password=password,
                is_client=True,
                region_code=requester.region_code,
                timezone=requester.timezone,
            )
            ActivityStream(customer=requester.customer, actor=requester.username,
                           verb='created_client_portal_access_credentials',
                           action_object=self.__str__()).save()

            self.client_user_obj = client_user_obj
            self.save()
            emailer.send_client_credential_email(self, password, requester)

    def revoke_client_portal(self, requester: User):
        if self.client_user_obj is not None:
            self.client_user_obj.is_active = False
            self.client_user_obj.save()
            ActivityStream(customer=requester.customer, actor=requester.username,
                           verb='revoked_client_portal',
                           action_object=self.__str__()).save()

    def enable_client_portal(self, requester: User):
        if self.client_user_obj is not None:
            self.client_user_obj.is_active = True
            self.client_user_obj.save()
            ActivityStream(customer=requester.customer, actor=requester.username,
                           verb='enabled_client_portal_access', action_object=self.__str__()).save()

    def set_permissions_to_team_after_creation(self):
        for user in User.objects.filter(Q(is_owner=True) | Q(is_team=True)):
            assign_perm(Client.CAN_VIEW, user, self)
            assign_perm(Client.CAN_EDIT, user, self)
            assign_perm(Client.CAN_DELETE, user, self)
            if user.is_clinician:
                assign_perm(Client.CAN_NOTES, user, self)

    def check_if_user_has_permissions(self, permission, user: User):
        if not user.has_perm(permission, self):
            raise PermissionDenied()

    def deny_permission_if_scheduler(self, user: User):
        if not user.is_scheduler:
            raise PermissionDenied()

    def toggle_portal_access(self, request: HttpRequest):
        if self.access_client_portal:
            self.access_client_portal = False
            self.save()
            if self.client_user_obj is not None:
                self.revoke_client_portal(requester=request.user)
            messages.success(request, 'Client Portal access revoked Successfully')
        else:
            if self.client_user_obj is None:
                self.access_client_portal = True
                self.save()
                self.create_client_portal_credentials(requester=request.user)
                messages.success(request, 'Client Portal access granted Successfully')
            else:
                self.access_client_portal = True
                self.save()
                self.enable_client_portal(requester=request.user)
                messages.success(request, 'Client Portal access granted Successfully')


class ClientAdministrativeNote(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    administrative_note_body = RichTextField(max_length=5000, null=True, blank=True)

    created_datetime = models.DateTimeField(auto_now=False, default=timezone.now)
    last_modified_datetime = models.DateTimeField(auto_now_add=False, default=timezone.now)
    last_modified_by = models.CharField(max_length=50, blank=True, null=True)


class EmailTemplates(models.Model):
    import codecs
    appointment_reminder_default = codecs.open(
        os.path.join(settings.BASE_DIR, "templates/email_default/appointment_reminder.html"
                     ), "r", 'utf-8').read()
    appointment_canceled_default = codecs.open(
        os.path.join(settings.BASE_DIR, "templates/email_default/appointment_canceled.html"
                     ), "r", 'utf-8').read()
    appointment_reschedule_default = codecs.open(
        os.path.join(settings.BASE_DIR, "templates/email_default/appointment_reschedule.html"
                     ), "r", 'utf-8').read()
    client_onboarding_default = codecs.open(
        os.path.join(settings.BASE_DIR, "templates/email_default/client_onboarding.html"
                     ), "r", 'utf-8').read()
    new_appointment_default = codecs.open(
        os.path.join(settings.BASE_DIR, "templates/email_default/new_appointment.html"
                     ), "r", 'utf-8').read()

    REMINDER_CHOICES = (
        ('12', '12 Hours'),
        ('24', '24 Hours'),
        ('48', '48 Hours'),
        ('None', 'Manually Send'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    appointment_reminder = RichTextField(
        max_length=10000, null=True, blank=True, default=appointment_reminder_default)

    new_appointment = RichTextField(
        max_length=10000, null=True, blank=True, default=new_appointment_default)

    appointment_reschedule = RichTextField(
        max_length=10000, null=True, blank=True, default=appointment_reschedule_default)

    appointment_canceled = RichTextField(
        max_length=10000, null=True, blank=True, default=appointment_canceled_default)

    client_onboarding = RichTextField(
        max_length=10000, null=True, blank=True, default=client_onboarding_default)

    email_reminder_setting = models.CharField(max_length=20, default=REMINDER_CHOICES[3][0], choices=REMINDER_CHOICES)


class ProjectUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Client, on_delete=models.CASCADE)


class ProjectGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey(Client, on_delete=models.CASCADE)


def upload_path(instance, file_name):
    return str(instance.customer.id)+'/client_files/{}/{}'.format(instance.client.uuid, file_name)


class ClientFile(TenantModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    tenant_id = 'customer_id'
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    client = TenantForeignKey(Client, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_path, validators=[validate_file_infection])
    file_name = models.CharField(max_length=50)
    uploaded_by = models.CharField(max_length=50)
    created_datetime = models.DateTimeField(auto_now=False, default=timezone.now)

    def get_delete_url(self):
        return reverse('clients:client-file-delete', kwargs={'uuid': self.uuid})

    def get_download_url(self):
        return reverse('clients:client-file-download', kwargs={'uuid': self.uuid})


class ClientEmails(TenantModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    tenant_id = 'customer_id'
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=100)
    email = models.CharField(max_length=1000)
    sent_by = models.CharField(max_length=50)
    sent_from_email = models.CharField(max_length=50)
    sent_to_email = models.CharField(max_length=50)
    sent_datetime = models.DateTimeField(auto_now=False, default=timezone.now)
    status = models.CharField(max_length=10)


class ClientNote(TenantModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    tenant_id = 'customer_id'
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    client = TenantForeignKey(Client, on_delete=models.CASCADE)
    client_note_title = models.CharField(max_length=500)
    client_note_body = RichTextField(max_length=5000, null=True, blank=True)

    created_by = models.CharField(max_length=50, blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now=False, default=timezone.now)
    last_modified_datetime = models.DateTimeField(auto_now_add=False, default=timezone.now)
    last_modified_by = models.CharField(max_length=50, blank=True, null=True)

    def get_delete_url(self):
        return reverse('clients:note-delete', kwargs={'uuid': self.uuid})

    def get_update_url(self):
        return reverse('clients:note-update', kwargs={'uuid': self.uuid})

    def delete_client_note(self, request: HttpRequest):
        self.client.check_if_user_has_permissions(self.client.CAN_DELETE, request.user)
        self.delete()
        messages.success(request, 'Note deleted successfully')
        ActivityStream(customer=request.user.customer, actor=request.user.username,
                       verb='deleted_note', action_object=self.uuid, target=self.client.__str__()).save()
