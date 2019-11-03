from django.urls import path
from appointments.views import AppointmentCreateView, CalendarView, AppointmentUpdateView, AppointmentStatusView, AppointmentDeleteView
from appointments.api import AppointmentsList, AppointmentsCURD

app_name = 'appointments'
urlpatterns = [
    path('', CalendarView.as_view(), name='calendar-view'),
    path('create/<uuid:uuid>/', AppointmentCreateView.as_view(), name='appointment-create'),
    path('update/<uuid:uuid>/', AppointmentUpdateView.as_view(), name='appointment-update'),
    path('delete/<uuid:uuid>/', AppointmentDeleteView.as_view(), name='appointment-delete'),
    path('<uuid:uuid>/<str:status>/status', AppointmentStatusView.as_view(), name='appointment-status'),

    path('api/list/<str:username>/', AppointmentsList.as_view(), name='api-list'),
    path('api/list/', AppointmentsList.as_view(), name='api-list-all'),
    path('api/<uuid:uuid>', AppointmentsCURD.as_view(), name='api-view'),
]
