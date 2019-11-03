from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from appointments.models import Appointment
from customers.models import ActivityStream
from appointments.forms import AppointmentForm, AppointmentUpdateForm
from clients.models import Client
from accounts.models import User
from django.core.exceptions import PermissionDenied
from zpractice_citus.custom_mixins import LoginRequiredNotClientMixin
from django.db.models import Q
from django.utils.timezone import make_aware
from datetime import datetime
import pytz
from clients import emailer


class CalendarView(LoginRequiredNotClientMixin, View):
    template_name = 'appointments/calendar_view.html'

    def get(self, request, *args, **kwargs):

        all_team = User.objects.filter(Q(is_team=True)|Q(is_owner=True))
        context = {
            'teams': all_team,
        }
        return render(request, self.template_name, context)


class AppointmentCreateView(LoginRequiredNotClientMixin, View):
    template_name = 'appointments/appointment_create.html'

    def get(self, request, uuid=None, *args, **kwargs):
        client = get_object_or_404(Client, uuid=uuid)

        if not request.user.has_perm(Client.CAN_VIEW, client):
            raise PermissionDenied

        if not self.request.user.is_scheduler:
            raise PermissionDenied

        qs = User.objects.filter(Q(is_owner=True) | Q(is_team=True))
        form = AppointmentForm()
        form.fields['assigned_to'].choices = [(user.username, user.first_name+' '+user.last_name) for user in qs.all()]
        form.fields['appointment_status'] = 'scheduled'
        context = {
            'form': form,
            'client': client,
        }
        return render(request, self.template_name, context)

    def post(self, request, uuid=None, *args, **kwargs):
        client = get_object_or_404(Client, uuid=uuid)

        if not request.user.has_perm(Client.CAN_VIEW, client):
            raise PermissionDenied

        form = AppointmentForm(request.POST or None)
        qs = User.objects.filter(Q(is_owner=True) | Q(is_team=True))
        form.fields['assigned_to'].choices = [(user.username, user.first_name + ' ' + user.last_name) for user in
                                              qs.all()]
        if form.is_valid():
            appointment = Appointment()
            appointment.client = client
            appointment.appointment_date = form.cleaned_data['appointment_date']
            appointment.appointment_time = form.cleaned_data['appointment_time']
            appointment.appointment_duration = form.cleaned_data['appointment_duration']
            appointment.appointment_reason = form.cleaned_data['appointment_reason']
            appointment.assigned_to = get_object_or_404(User, username=form.cleaned_data['assigned_to'])

            appointment.set_aware_appointment_datetime_utc(request.user.timezone)

            if form.cleaned_data['send_confirmation_email']:
                emailer.send_appointment_created_email(appointment, request.user)
            appointment.save()
            messages.success(request, 'Appointment deleted successfully')
            ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                           verb='created_appointment', action_object=appointment.get_human_readable_datetime(),
                           target=client.__str__()).save()

            return redirect('clients:client-appointments', uuid=client.uuid)
        messages.error(request, 'There was an error Creating appointment')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)


class AppointmentUpdateView(LoginRequiredNotClientMixin, View):
    template_name = "appointments/appointment_edit.html"

    def get_queryset(self, uuid):
        appointment = get_object_or_404(Appointment, uuid=uuid)
        if not self.request.user.has_perm(Client.CAN_VIEW, appointment.client):
            raise PermissionDenied
        if not self.request.user.is_scheduler:
            raise PermissionDenied()
        return appointment

    def get(self, request, uuid=None, *args, **kwargs):
        appointment = self.get_queryset(uuid=uuid)
        form = AppointmentUpdateForm()
        qs = User.objects.filter(Q(is_owner=True) | Q(is_team=True))
        form.fields['assigned_to'].choices = [(user.username, user.first_name + ' ' + user.last_name) for user in
                                              qs.all()]
        form.initial = {
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'appointment_duration': appointment.appointment_duration,
            'appointment_reason': appointment.appointment_reason,
            'assigned_to': appointment.assigned_to,
            'appointment_status': appointment.appointment_status,
        }
        context = {
            'form': form,
            'appointment': appointment,
        }
        return render(request, self.template_name, context)

    def post(self, request, uuid=None, *args, **kwargs):
        appointment = self.get_queryset(uuid=uuid)
        form = AppointmentUpdateForm(request.POST or None)
        qs = User.objects.filter(Q(is_owner=True) | Q(is_team=True))
        form.fields['assigned_to'].choices = [(user.username, user.first_name + ' ' + user.last_name) for user in
                                              qs.all()]
        if form.is_valid():
            old_date = appointment.appointment_date
            old_time = appointment.appointment_time
            appointment.appointment_date = form.cleaned_data['appointment_date']
            appointment.appointment_time = form.cleaned_data['appointment_time']
            appointment.appointment_duration = form.cleaned_data['appointment_duration']
            appointment.appointment_reason = form.cleaned_data['appointment_reason']
            appointment.assigned_to = get_object_or_404(User, username=form.cleaned_data['assigned_to'])
            appointment.status_setter(form.cleaned_data['appointment_status'])

            nieve_dt = datetime.combine(form.cleaned_data['appointment_date'], form.cleaned_data['appointment_time'])
            appointment_datetime_utc = make_aware(nieve_dt, timezone=pytz.timezone(request.user.timezone))
            appointment.appointment_datetime_utc = appointment_datetime_utc

            appointment.save()
            messages.success(request, 'Appointment updated successfully')

            ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                           verb='modified_appointment', action_object=appointment.get_human_readable_datetime(),
                           target=appointment.client.__str__()).save()

            if old_time != form.cleaned_data['appointment_time'] or old_date != form.cleaned_data['appointment_date']:
                if form.cleaned_data['send_reschedule_email']:
                    emailer.send_appointment_reschedule_email(appointment, old_date, old_time, request.user)

            return redirect('appointments:calendar-view')

        messages.error(request, 'There was an error updating appointment')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)


class AppointmentStatusView(LoginRequiredNotClientMixin, View):
    '''
        Scheduled = #96b3e6
        show = #a0ff87
        no show = #f57373
        canceled = #f0a0f5
        late_canceled = #f5eb82
    '''

    def get_queryset(self, uuid):
        appointment = get_object_or_404(Appointment, uuid=uuid)
        if not self.request.user.has_perm(Client.CAN_VIEW, appointment.client):
            raise PermissionDenied
        if not self.request.user.is_owner:
            owner = self.request.user.team_relation.owner
            if not self.request.user.team_relation.is_scheduler:
                raise PermissionDenied
        else:
            owner = self.request.user
        return appointment, owner

    def get(self, request, uuid=None, status=None, *args, **kwargs):
        appointment, owner = self.get_queryset(uuid=uuid)
        if status == 'scheduled':
            appointment.set_scheduled()
            messages.info(request, 'Appointment status changed to Scheduled')
        elif status == 'show':
            appointment.set_show()
            messages.info(request, 'Appointment status changed to Show')
        elif status == 'no_show':
            appointment.set_no_show()
            messages.info(request, 'Appointment status changed to No Show')
        elif status == 'canceled':
            appointment.set_canceled()
            messages.info(request, 'Appointment status changed to Canceled')
        elif status == 'late_canceled':
            appointment.set_late_canceled()
            messages.info(request, 'Appointment status changed to Late Canceled')
        appointment.save()
        return redirect('appointments:calendar-view')


class AppointmentDeleteView(LoginRequiredNotClientMixin, DeleteView):
    template_name = "appointments/appointment_delete.html"
    model = Appointment
    success_url = reverse_lazy('appointments:calendar-view')

    def get_object(self, queryset=None):
        appointment = get_object_or_404(Appointment, uuid=self.kwargs['uuid'])
        if not self.request.user.has_perm(Client.CAN_DELETE, appointment.client):
            raise PermissionDenied()
        if not self.request.user.is_scheduler:
            raise PermissionDenied()

        return appointment

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        action_object = self.object.get_human_readable_datetime()
        self.object.delete()
        messages.success(request, 'Appointment deleted succesfully')
        if self.request.POST.get('canceled_checkbox'):
            emailer.send_appointment_canceled_email(self.object, self.request.user)

        ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                       verb='deleted_appointment', action_object=action_object,
                       target=self.object.client.__str__()).save()
        return HttpResponseRedirect(success_url)
