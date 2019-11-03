import pytz
from django.db import models
from django.shortcuts import reverse
from django.utils.timezone import datetime, make_aware

from clients.models import Client
import uuid
from django.utils import timezone
from accounts.models import User
from customers.models import Customer
from django_multitenant.fields import *
from django_multitenant.models import *


class Appointment(TenantModel):
    STATUS_TYPE = [
        ('scheduled', 'Scheduled'),
        ('show', 'Show'),
        ('no_show', 'No Show'),
        ('canceled', 'Canceled'),
        ('late_canceled', 'Late Canceled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    tenant_id = 'customer_id'
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    client = TenantForeignKey(Client, on_delete=models.CASCADE)
    all_day = models.BooleanField(default=False)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    appointment_datetime_utc = models.DateTimeField(null=True)
    appointment_duration = models.DurationField()
    appointment_reason = models.CharField(max_length=1000)
    appointment_status = models.CharField(max_length=50, choices=STATUS_TYPE, default='scheduled')
    assigned_to = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_by = models.CharField(max_length=50)
    created_datetime = models.DateTimeField(auto_now=False, default=timezone.now)
    last_modified_datetime = models.DateTimeField(auto_now_add=False, default=timezone.now)
    last_modified_by = models.CharField(max_length=50)
    colour = models.CharField(max_length=20, default='#96b3e6')
    '''
    Scheduled = #96b3e6
    show = #a0ff87
    no show = #c8c8c8
    canceled = #f09b50
    late_canceled = #ff8487
    '''


    def __str__(self):
        return "{} {}".format(self.client.first_name, self.client.last_name)

    def set_aware_appointment_datetime_utc(self, user_timezone):
        nieve_dt = datetime.combine(self.appointment_date, self.appointment_time)
        appointment_datetime_utc = make_aware(nieve_dt, timezone=pytz.timezone(user_timezone))
        self.appointment_datetime_utc = appointment_datetime_utc

    def get_human_readable_datetime(self):
        return self.appointment_datetime_utc.strftime("%d %b %Y, %I:%M %p")

    def get_update_url(self):
        return reverse('appointments:appointment-update', kwargs={'uuid': self.uuid})

    def get_delete_url(self):
        return reverse('appointments:appointment-delete', kwargs={'uuid': self.uuid})

    def appointment_start_datetime(self):
        return self.appointment_datetime_utc

    def appointment_end_datetime(self):
        return self.appointment_datetime_utc + self.appointment_duration

    def set_scheduled(self):
        self.appointment_status = 'scheduled'
        self.colour = '#96b3e6'

    def set_show(self):
        self.appointment_status = 'show'
        self.colour = '#a0ff87'

    def set_no_show(self):
        self.appointment_status = 'no_show'
        self.colour = '#c8c8c8'

    def set_canceled(self):
        self.appointment_status = 'canceled'
        self.colour = '#f09b50'

    def set_late_canceled(self):
        self.appointment_status = 'late_canceled'
        self.colour = '#ff8487'

    def status_setter(self, status):
        if status == 'show':
            self.set_show()
        elif status == 'no_show':
            self.set_show()
        elif status == 'canceled':
            self.set_canceled()
        elif status == 'late_canceled':
            self.set_late_canceled()

    def status_getter(self,):
        if self.appointment_status == 'show':
            return 'Show'
        elif self.appointment_status == 'no_show':
            return 'No Show'
        elif self.appointment_status == 'canceled':
            return 'Canceled'
        elif self.appointment_status == 'late_canceled':
            return 'Late Canceled'

    def get_scheduled_url(self):
        return reverse('appointments:appointment-status', kwargs={'uuid': self.uuid, 'status': 'scheduled'})

    def get_show_url(self):
        return reverse('appointments:appointment-status', kwargs={'uuid': self.uuid, 'status': 'show'})

    def get_no_show_url(self):
        return reverse('appointments:appointment-status', kwargs={'uuid': self.uuid, 'status': 'no_show'})

    def get_canceled_url(self):
        return reverse('appointments:appointment-status', kwargs={'uuid': self.uuid, 'status': 'canceled'})

    def get_late_canceled_url(self):
        return reverse('appointments:appointment-status', kwargs={'uuid': self.uuid, 'status': 'late_canceled'})
