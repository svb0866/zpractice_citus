from django.db import models
from django.utils import timezone
import pytz
from django_multitenant.models import TenantModel
from phonenumbers import parse, format_number, PhoneNumberFormat
import uuid


class Customer(TenantModel):
    username = models.CharField(max_length=50, unique=True)
    tenant_id = 'id'
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=100, unique=True)

    created_on = models.DateTimeField(auto_now=False, default=timezone.now)
    last_modified = models.DateTimeField(auto_now_add=False, default=timezone.now)

    '''paid_until = models.DateField()
    on_trial = models.BooleanField()'''

    timezone = models.CharField(max_length=100, choices=[(t, t) for t in pytz.common_timezones])
    region_code = models.CharField(max_length=10)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def get_parsed_phone(self):
        if self.phone is not None:
            ph = parse(self.phone)
            return format_number(ph, PhoneNumberFormat.INTERNATIONAL)
        return None


class ActivityStream(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    activity_logged_on = models.DateTimeField(auto_now=False, default=timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    actor = models.CharField(max_length=200, null=True)
    verb = models.CharField(max_length=200, null=True)
    action_object = models.CharField(max_length=200, null=True)
    target = models.CharField(max_length=200, null=True)

    # Sachin (actor) created (verb) appointment (object) for dr.vinayak (target) 12 hours ago

    def __str__(self):
        self.actor + " " + self.verb + " " + self.action_object + "--" + self.target + " " + self.activity_logged_on.strftime(
            "%d %b %Y, %I:%M %p")