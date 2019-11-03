from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils import timezone
from django.urls import reverse
from customers.models import Customer, ActivityStream
import pytz
from phonenumbers import parse, format_number, PhoneNumberFormat
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django_multitenant.fields import *
from django_multitenant.models import *


def login_do_stuff(sender, user, request, **kwargs):
    ActivityStream(customer=user.customer, actor=user.username,
                   verb='logged in').save()
    user.unsuccessful_login_attempts = 0
    user.save()


def logout_do_stuff(sender, user, request, **kwargs):
    ActivityStream(customer=user.customer, actor=user.username,
                   verb='logged out').save()


def login_failed_do_stuff(sender, request, **kwargs):
    ActivityStream(customer=Customer.objects.get(pk=1), actor='unknown',
                   verb='login_failed' + request.META['HTTP_HOST'], target=request.POST['username']).save()
    user = User.objects.filter(username=request.POST['username'])
    if user.exists():
        user = user.first()
        user.unsuccessful_login_attempts += 1
        user.save()

        if user.unsuccessful_login_attempts > 10:
            ActivityStream(customer=user.customer, actor='unknown',
                           verb='Login_fail_exceeded_10times_account_disabled', target=user.username).save()
            user.is_active = False
            user.save()


user_logged_in.connect(login_do_stuff)
user_logged_out.connect(logout_do_stuff)
user_login_failed.connect(login_failed_do_stuff)


class UserManager(BaseUserManager):
    def create_user(self, customer=None, username=None, email=None, password=None, first_name=None,
                    last_name=None, phone=None, is_owner=False, is_team=False, is_client=False, is_clinician=False, is_scheduler=False,
                    is_biller=False, region_code=None, timezone=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have an password ')
        if not first_name:
            raise ValueError('Users must have an First name ')
        if not last_name:
            raise ValueError('Users must have an Last name ')
        if not phone:
            raise ValueError('Users must have an Phone number ')
        if not username:
            raise ValueError('Users must have an Username ')

        user = User(email=self.normalize_email(email))
        user.customer = customer
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.set_password(password)
        user.is_owner = is_owner
        user.is_team = is_team
        user.is_client = is_client

        user.is_clinician = is_clinician
        user.is_scheduler = is_scheduler
        user.is_biller = is_biller
        user.region_code = region_code
        user.timezone = timezone
        user.save(using=self._db)

        if not user.is_client:
            from clients.models import EmailTemplates
            EmailTemplates(user=user).save()
        return user

    def create_staffuser(self, username, email, password, first_name, last_name, phone):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(username=username, email=email, password=password, first_name=first_name,
                                last_name=last_name, phone=phone)
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, first_name, last_name, phone):
        """
        Creates and saves a superuser with the given email and password.
        """

        user = self.create_user(username=username, email=email, password=password, first_name=first_name,
                                last_name=last_name, phone=phone)
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

    def get_queryset(self):
        # Injecting tenant_id filters in the get_queryset.
        # Injects tenant_id filter on the current model for all the non-join/join queries.
        queryset = self._queryset_class(self.model)
        current_tenant = get_current_tenant()
        if current_tenant:
            kwargs = get_tenant_filters(self.model)
            return queryset.filter(**kwargs)
        return queryset


class User(TenantModel, AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    tenant_id = 'customer_id'
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=255)

    created_datetime = models.DateTimeField(auto_now=False, default=timezone.now)
    last_modified = models.DateTimeField(auto_now_add=False, default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # a admin user; non super-user
    is_admin = models.BooleanField(default=False) # a superuser

    is_owner = models.BooleanField(default=False)
    is_team = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)

    is_clinician = models.BooleanField(default=False)
    is_scheduler = models.BooleanField(default=False)
    is_biller = models.BooleanField(default=False)
    # notice the absence of a "Password field", that's built in.

    unsuccessful_login_attempts = models.IntegerField(default=0)

    timezone = models.CharField(max_length=100, choices=[(t, t) for t in pytz.common_timezones])
    region_code = models.CharField(max_length=10)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone']  # Username Password are required by default.

    class Meta(object):
        unique_together = ["id", "customer"]

    def get_full_name(self):
        return self.first_name + self.last_name

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.first_name + " " +self.last_name

    def get_last5_clients(self):
        if not self.is_client:
            from clients.models import Client
            return Client.objects.filter().order_by('-created_datetime')[:5]

    def update_team_member(self):
        if self.is_owner:
            return None
        return reverse('team-update', kwargs={'username': self.username})

    def delete_team_member(self):
        if self.is_owner:
            return None
        return reverse('team-delete', kwargs={'username': self.username})

    def get_parsed_phone(self):
        if self.phone is not None:
            ph = parse(self.phone)
            return format_number(ph, PhoneNumberFormat.INTERNATIONAL)
        return None

    def get_tenant_for_user(self):
        return self.customer

