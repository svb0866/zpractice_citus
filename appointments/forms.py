from django import forms


class AppointmentForm(forms.Form):
    STATUS_TYPE = [
        ('scheduled', 'Scheduled'),
        ('show', 'Show'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
        ('late_canceled', 'Late Canceled'),
    ]
    USER = [
        ('None', 'None')
    ]
    DURATION = [
        ('1:00:00', '60 Min'),
        ('00:05:00', '5 Min'),
        ('00:10:00', '10 Min'),
        ('00:15:00', '15 Min'),
        ('00:20:00', '20 Min'),
        ('00:25:00', '25 Min'),
        ('00:30:00', '30 Min'),
        ('00:35:00', '35 Min'),
        ('00:40:00', '40 Min'),
        ('00:45:00', '45 Min'),
        ('00:50:00', '50 Min'),
        ('01:00:00', '1 Hour'),
        ('01:05:0', '1 Hour 5 Min'),
        ('01:10:00', '1 Hour 10 Min'),
        ('01:15:00', '1 Hour 15 Min'),
        ('01:20:00', '1 Hour 20 Min'),
        ('01:25:00', '1 Hour 25 Min'),
        ('01:30:00', '1 Hour 30 Min'),
        ('01:35:00', '1 Hour 35 Min'),
        ('01:40:00', '1 Hour 40 Min'),
        ('01:45:00', '1 Hour 45 Min'),
        ('01:50:00', '1 Hour 50 Min'),
        ('01:55:00', '1 Hour 55 Min'),
        ('02:00:00', '2 Hour'),
        ('02:05:0', '2 Hour 5 Min'),
        ('02:10:00', '2 Hour 10 Min'),
        ('02:15:00', '2 Hour 15 Min'),
        ('02:20:00', '2 Hour 20 Min'),
        ('02:25:00', '2 Hour 25 Min'),
        ('02:30:00', '2 Hour 30 Min'),
        ('02:35:00', '2 Hour 35 Min'),
        ('02:40:00', '2 Hour 40 Min'),
        ('02:45:00', '2 Hour 45 Min'),
        ('02:50:00', '2 Hour 50 Min'),
        ('02:55:00', '2 Hour 55 Min'),
        ('03:00:00', '3 Hour'),
        ('03:05:0', '3 Hour 5 Min'),
        ('03:10:00', '3 Hour 10 Min'),
        ('03:15:00', '3 Hour 15 Min'),
        ('03:20:00', '3 Hour 20 Min'),
        ('03:25:00', '3 Hour 25 Min'),
        ('03:30:00', '3 Hour 30 Min'),
        ('03:35:00', '3 Hour 35 Min'),
        ('03:40:00', '3 Hour 40 Min'),
        ('03:45:00', '3 Hour 45 Min'),
        ('03:50:00', '3 Hour 50 Min'),
        ('03:55:00', '3 Hour 55 Min'),
        ('04:00:00', '4 Hour'),
        ('04:05:0', '4 Hour 5 Min'),
        ('04:10:00', '4 Hour 10 Min'),
        ('04:15:00', '4 Hour 15 Min'),
        ('04:20:00', '4 Hour 20 Min'),
        ('04:25:00', '4 Hour 25 Min'),
        ('04:30:00', '4 Hour 30 Min'),
        ('04:35:00', '4 Hour 35 Min'),
        ('04:40:00', '4 Hour 40 Min'),
        ('04:45:00', '4 Hour 45 Min'),
        ('04:50:00', '4 Hour 50 Min'),
        ('04:55:00', '4 Hour 55 Min'),
        ('05:00:00', '5 Hour'),
        ('05:05:0', '5 Hour 5 Min'),
        ('05:10:00', '5 Hour 10 Min'),
        ('05:15:00', '5 Hour 15 Min'),
        ('05:20:00', '5 Hour 20 Min'),
        ('05:25:00', '5 Hour 25 Min'),
        ('05:30:00', '5 Hour 30 Min'),
        ('05:35:00', '5 Hour 35 Min'),
        ('05:40:00', '5 Hour 40 Min'),
        ('05:45:00', '5 Hour 45 Min'),
        ('05:50:00', '5 Hour 50 Min'),
        ('05:55:00', '5 Hour 55 Min'),
        ('06:00:00', '6 Hour'),
        ('06:05:0', '6 Hour 5 Min'),
        ('06:10:00', '6 Hour 10 Min'),
        ('06:15:00', '6 Hour 15 Min'),
        ('06:20:00', '6 Hour 20 Min'),
        ('06:25:00', '6 Hour 25 Min'),
        ('06:30:00', '6 Hour 30 Min'),
        ('06:35:00', '6 Hour 35 Min'),
        ('06:40:00', '6 Hour 40 Min'),
        ('06:45:00', '6 Hour 45 Min'),
        ('06:50:00', '6 Hour 50 Min'),
        ('06:55:00', '6 Hour 55 Min'),
        ('07:00:00', '7 Hour'),
        ('07:30:00', '7 Hour 30 Min'),
        ('08:00:00', '8 Hour'),
        ('08:30:00', '8 Hour 30 Min'),
        ('09:00:00', '9 Hour'),
        ('09:30:00', '9 Hour 30 Min'),
        ('10:00:00', '10 Hour'),
        ('11:00:00', '11 Hour'),
        ('12:00:00', '12 Hour'),
    ]

    appointment_date = forms.DateField()
    appointment_time = forms.TimeField(widget=forms.TimeInput(format='%I:%M %p'))
    appointment_duration = forms.ChoiceField(choices=DURATION)
    appointment_reason = forms.CharField()
    assigned_to = forms.ChoiceField(choices=USER)
    send_confirmation_email = forms.BooleanField(initial=True, required=False)


class AppointmentUpdateForm(AppointmentForm):
    STATUS_TYPE = [
        ('scheduled', 'Scheduled'),
        ('show', 'Show'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
        ('late_canceled', 'Late Canceled'),
    ]
    appointment_status = forms.ChoiceField(choices=STATUS_TYPE)
    send_reschedule_email = forms.BooleanField(initial=True, required=False)


