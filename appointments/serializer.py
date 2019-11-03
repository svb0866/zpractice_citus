from rest_framework import serializers
from appointments.models import Appointment


class CalendarEventsSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True, source='uuid')
    allDay = serializers.BooleanField(source='all_day')
    start = serializers.DateTimeField(source='appointment_start_datetime')
    end = serializers.DateTimeField(source='appointment_end_datetime')
    title = serializers.CharField(source='__str__')
    color = serializers.CharField(source='colour')


class AppointmentSerializer(serializers.Serializer):
    STATUS_TYPE = [
        ('scheduled', 'Scheduled'),
        ('show', 'Show'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
        ('late_canceled', 'Late Canceled'),
    ]

    uuid = serializers.UUIDField(read_only=True)
    client = serializers.CharField(read_only=True, source='client.__str__')
    client_url = serializers.CharField(read_only=True, source='client.get_absolute_url')
    appointment_datetime = serializers.DateTimeField(source='get_human_readable_datetime')
    appointment_reason = serializers.CharField(max_length=100, allow_blank=True)
    assigned_to = serializers.CharField(max_length=50, source='assigned_to.__str__')
    created_by = serializers.CharField(read_only=True, allow_blank=True)
    created_datetime = serializers.DateTimeField(read_only=True)
    last_modified_datetime = serializers.DateTimeField(read_only=True)
    last_modified_by = serializers.CharField(read_only=True)

    colour = serializers.CharField()
    show_url = serializers.CharField(source='get_show_url')
    no_show_url = serializers.CharField(source='get_no_show_url')
    scheduled_url = serializers.CharField(source='get_scheduled_url')
    canceled_url = serializers.CharField(source='get_canceled_url')
    late_canceled_url = serializers.CharField(source='get_late_canceled_url')
