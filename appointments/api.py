from rest_framework import generics
from accounts.models import User
from clients.models import Client
from appointments.models import Appointment
from django.shortcuts import get_object_or_404
from guardian.shortcuts import get_objects_for_user
from django.core.exceptions import PermissionDenied
from appointments.serializer import CalendarEventsSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import request
from rest_framework import status
from appointments.serializer import CalendarEventsSerializer, AppointmentSerializer
from django.db.models import Q


class AppointmentsList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get_objects(self, start, end, username):
        if username is None:
            clients = get_objects_for_user(self.request.user, Client.CAN_VIEW, Client)
            appointments = Appointment.objects.filter(client__in=clients).filter(
                appointment_date__range=(start, end))
            return appointments
        else:
            selection = get_object_or_404(User, username=username)
            appointments = Appointment.objects.filter(assigned_to=selection)

            return appointments

    def get(self, request, username=None, format=None,):
        if request.user.is_authenticated:
            #print(request.GET) <- check this out!
            start_date = request.GET['start'].split('T')[0]

            end_date = request.GET['end'].split('T')[0]

            serializer = CalendarEventsSerializer(self.get_objects(start_date, end_date, username), many=True,)
            return Response(serializer.data)
        raise PermissionDenied


class AppointmentsCURD(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get_object(self, uuid):
        appointment = get_object_or_404(Appointment, uuid=uuid)
        if self.request.user.has_perm(Client.CAN_VIEW, appointment.client):
            return appointment
        raise PermissionDenied

    def get(self, request, uuid, format=None):
        if request.user.is_authenticated:
            serializer = AppointmentSerializer(self.get_object(uuid=uuid))
            return Response(serializer.data)
        raise PermissionDenied
