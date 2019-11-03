from django.contrib import admin
from django.urls import path
from clients.views import ClientListView, ClientDetailView, ClientAdministrativeNotesPostView, \
    ClientDeleteView, ClientCreateView, ClientUpdateView, ClientNoteUpdate, ClientNoteDelete, ClientFileUploadView, \
    ClientAppointmentsListView, ClientFileDeleteView, ClientPortalAccessToggleView, ClientFileDownloadView


app_name = 'clients'
urlpatterns = [
    path('', ClientListView.as_view(), name='clients-list'),
    path('<uuid:uuid>/', ClientDetailView.as_view(), name='client-detail'),
    path('<uuid:uuid>/administrativenote', ClientAdministrativeNotesPostView.as_view(), name='client-administrative-note'),
    path('<uuid:uuid>/delete/', ClientDeleteView.as_view(), name='client-delete'),
    path('create/', ClientCreateView.as_view(), name='client-create'),
    path('<uuid:uuid>/update/', ClientUpdateView.as_view(), name='client-update'),
    path('<uuid:uuid>/upload/', ClientFileUploadView.as_view(), name='client-file-upload'),
    path('file/delete/<uuid:uuid>', ClientFileDeleteView.as_view(), name='client-file-delete'),
    path('file/download/<uuid:uuid>', ClientFileDownloadView.as_view(), name='client-file-download'),
    path('<uuid:uuid>/appointments/', ClientAppointmentsListView.as_view(), name='client-appointments'),
    path('<uuid:uuid>/access/', ClientPortalAccessToggleView.as_view(), name='client-portal-access'),

    path('note/<uuid:uuid>/update', ClientNoteUpdate.as_view(), name='note-update'),
    path('note/<uuid:uuid>/delete', ClientNoteDelete.as_view(), name='note-delete'),


]
