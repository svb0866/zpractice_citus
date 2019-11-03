from django.core.files.storage import get_storage_class
from django.http import HttpResponseRedirect

from clients.models import Client, ClientAdministrativeNote, ClientNote
from clients.forms import ClientAdministrativeNoteForm, ClientNoteForm, ClientCreateForm, ClientUpdateForm, ClientEmailTemplateUpdateForm
from clients.forms import ClientFileUploadForm
from guardian.shortcuts import get_objects_for_user
from django.urls import reverse_lazy
from zpractice_citus.custom_mixins import LoginRequiredNotClientMixin
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.views.generic.list import ListView
from guardian.shortcuts import assign_perm
from django.core.exceptions import PermissionDenied
from accounts.models import User
from django.db.models import Q
from clients.models import EmailTemplates, ClientFile
from django.contrib import messages
from appointments.models import Appointment
from customers.models import ActivityStream


class ClientListView(LoginRequiredNotClientMixin, ListView):
    model = Client
    paginate_by = 20
    context_object_name = 'clients'
    template_name = 'clients/client_list.html'

    first_name = None
    last_name = None
    email = None
    phone = None

    def get_context_data(self, **kwargs):
        context = super(ClientListView, self).get_context_data(**kwargs)
        context['first_name'] = self.first_name
        context['last_name'] = self.last_name
        context['email'] = self.email
        context['phone'] = self.phone
        return context

    def get_queryset(self):
        #clients = get_objects_for_user(self.request.user, Client.CAN_VIEW, Client).order_by('last_modified')
        clients = Client.objects.all()
        if self.request.GET.get('first_name'):
            self.first_name = self.request.GET.get('first_name')
            clients = clients.filter(first_name__icontains=self.request.GET.get('first_name'))

        if self.request.GET.get('last_name'):
            self.last_name = self.request.GET.get('last_name')
            clients = clients.filter(last_name__icontains=self.request.GET.get('last_name'))

        if self.request.GET.get('email'):
            self.email = self.request.GET.get('email')
            if str(self.request.GET.get('email')).__contains__('@'):
                email = str(self.request.GET.get('email')).split('@')[0]
            else:
                email = str(self.request.GET.get('email'))
            clients = clients.filter(Q(primary_email__icontains=email) | Q(secondary_email__icontains=email))

        if self.request.GET.get('phone'):
            self.phone = self.request.GET.get('phone')
            clients = clients.filter(Q(phone1__icontains=self.request.GET.get('phone')) |
                                     Q(phone2__icontains=self.request.GET.get('phone')) |
                                     Q(phone3__contains=self.request.GET.get('phone')))

        return clients


class ClientDetailView(LoginRequiredNotClientMixin, View):
    template_name = 'clients/client_details.html'

    def get_queryset(self, uuid):
        client = get_object_or_404(Client, uuid=uuid)

        if not self.request.user.has_perm(Client.CAN_VIEW, client):
            raise PermissionDenied()

        try:
            administrative_note = client.clientadministrativenote
        except ObjectDoesNotExist:
            administrative_note = ClientAdministrativeNote(created_by=self.request.user, last_modified_by=self.request.user,
                                                           client=client)
            administrative_note.save()

        if self.request.user.is_clinician:
            client_notes = client.clientnote_set
        else:
            client_notes = None

        return client, administrative_note, client_notes

    def get(self, request, uuid=None):
        client, administrative_note, client_notes = self.get_queryset(uuid=uuid)

        client_note_form = ClientNoteForm()
        administrative_note_form = ClientAdministrativeNoteForm(administrative_note.__dict__)

        upload_form = ClientFileUploadForm()

        context = {
            'client': client,
            'administrative_note': administrative_note,
            'client_notes': client_notes,
            'administrative_note_form': administrative_note_form,
            'client_note_form': client_note_form,
            'upload_form': upload_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, uuid=None):
        client, administrative_note, client_notes = self.get_queryset(uuid=uuid)
        administrative_note_form = ClientAdministrativeNoteForm(administrative_note.__dict__)
        client_note_form = ClientNoteForm(self.request.POST or None)
        if client_note_form.is_valid():
            client_note = ClientNote()
            client_note.client_note_title = client_note_form.cleaned_data['client_note_title']
            client_note.client_note_body = client_note_form.cleaned_data['client_note_body']
            client_note.client = client
            client_note.created_by = self.request.user
            client_note.last_modified_by = self.request.user
            client_note.save()
            ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                           verb='created_client_note', action_object=client_note.uuid,
                           target=client_note.client.__str__()).save()
            messages.success(request, 'Client updated succesfully')
            return redirect('clients:client-detail', uuid=uuid)

        messages.error(request, 'There was an error updating client')
        context = {
            'client': client,
            'administrative_note': administrative_note,
            'client_notes': client_notes,
            'administrative_note_form': administrative_note_form,
            'client_note_form': client_note_form,
        }
        return render(request, self.template_name, context)


class ClientAdministrativeNotesPostView(LoginRequiredNotClientMixin, View):
    def post(self, request, uuid=None):
        client = get_object_or_404(Client, uuid=uuid)

        administrative_note_form = ClientAdministrativeNoteForm(request.POST)
        if administrative_note_form.is_valid():
            if administrative_note_form.cleaned_data.get('administrative_note_body') == '':
                administrative_note = client.clientadministrativenote
                administrative_note.administrative_note_body = ''
                administrative_note.save()
                messages.success(request, 'Administrative Note saved succesfully')
                ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                               verb='created_client_note', action_object=administrative_note.uuid,
                               target=administrative_note.client.__str__()).save()

            elif administrative_note_form.has_changed():
                administrative_note = client.clientadministrativenote
                administrative_note.administrative_note_body = administrative_note_form.cleaned_data.get('administrative_note_body')
                administrative_note.save()
                messages.success(request, 'Administrative Note saved succesfully')
                ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                               verb='created_client_note', action_object=administrative_note.uuid,
                               target=administrative_note.client.__str__()).save()
            else:
                messages.error(request, 'There was an error updating Administrative note')
            return redirect('clients:client-detail', uuid=uuid)


class ClientDeleteView(LoginRequiredNotClientMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('clients:clients-list')
    context_object_name = 'client'
    template_name = 'clients/client_delete.html'

    def get_object(self, queryset=None):
        client = get_object_or_404(Client, uuid=self.kwargs['uuid'])
        if not self.request.user.has_perm(Client.CAN_DELETE, client):
            raise PermissionDenied()
        return client

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, 'Client deleted successfully')
        ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                       verb='deleted_client', action_object=self.object).save()
        return HttpResponseRedirect(success_url)


class ClientCreateView(LoginRequiredNotClientMixin, CreateView):
    model = Client
    template_name = 'clients/client_create.html'
    form_class = ClientCreateForm

    def get_form(self, form_class=None):
        form = super(ClientCreateView, self).get_form(form_class)
        form.fields['phone1'].widget.attrs['data-default-code'] = self.request.user.region_code
        form.fields['phone2'].widget.attrs['data-default-code'] = self.request.user.region_code
        form.fields['phone3'].widget.attrs['data-default-code'] = self.request.user.region_code
        return form

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        client = Client(**form.cleaned_data)
        client.created_by = self.request.user.username
        client.last_modified_by = self.request.user.username
        client.save()
        messages.success(self.request, 'Client created successfully')
        ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                       verb='created_client', action_object=client).save()
        client.set_permissions_to_team_after_creation()
        if client.access_client_portal:
            client.create_client_portal_credentials(requester=self.request.user)

        return redirect('clients:clients-list')

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        messages.error(self.request, 'There was an error creating client')
        return self.render_to_response(self.get_context_data(form=form))


class ClientUpdateView(LoginRequiredNotClientMixin, UpdateView):
    model = Client
    template_name = 'clients/client_update.html'
    form_class = ClientUpdateForm

    def get_form(self, form_class=None):
        form = super(ClientUpdateView, self).get_form(form_class)
        form.fields['phone1'].widget.attrs['data-default-code'] = self.request.user.region_code
        form.fields['phone2'].widget.attrs['data-default-code'] = self.request.user.region_code
        form.fields['phone3'].widget.attrs['data-default-code'] = self.request.user.region_code
        return form

    def get_object(self, queryset=None):
        client = get_object_or_404(Client, uuid=self.kwargs['uuid'])
        if not self.request.user.has_perm(Client.CAN_EDIT, client):
            raise PermissionDenied()
        client.last_modified_by = self.request.user.username
        return client

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.success(self.request, 'Client updated successfully')
        ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                       verb='updated_client', action_object=self.object).save()
        return super().form_valid(form)

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        messages.error(self.request, 'There was an error updating client')
        return self.render_to_response(self.get_context_data(form=form))


class ClientNoteUpdate(LoginRequiredNotClientMixin, View):
    template_name = 'clients/client_details.html'

    def get(self, request, uuid=None):
        client_note = get_object_or_404(ClientNote, uuid=uuid)
        client = client_note.client
        administrative_note = client.clientadministrativenote
        client.check_if_user_has_permissions(Client.CAN_NOTES, user=request.user)
        client_notes = client.clientnote_set
        client_note_form = ClientNoteForm(client_note.__dict__)
        administrative_note_form = ClientAdministrativeNoteForm(administrative_note.__dict__)

        context = {
            'client': client,
            'administrative_note': administrative_note,
            'client_notes': client_notes,
            'administrative_note_form': administrative_note_form,
            'client_note_form': client_note_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, uuid=None):
        client_note = get_object_or_404(ClientNote, uuid=uuid)
        client = client_note.client
        administrative_note = client.clientadministrativenote
        client.check_if_user_has_permissions(Client.CAN_NOTES, request.user)
        client_notes = client.clientnote_set
        administrative_note_form = ClientAdministrativeNoteForm(administrative_note.__dict__)
        client_note_form = ClientNoteForm(self.request.POST or None)
        if client_note_form.is_valid():
            client_note.client_note_title = client_note_form.cleaned_data['client_note_title']
            client_note.client_note_body = client_note_form.cleaned_data['client_note_body']
            client_note.last_modified_by = self.request.user.username
            client_note.save()
            messages.success(request, 'Client note saved successfully')
            ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                           verb='updated_note', action_object=client_note.uuid, target=client.__str__()).save()
            return redirect('clients:client-detail', uuid=client.uuid)

        messages.error(request, 'There was an error saving note')
        context = {
            'client': client,
            'administrative_note': administrative_note,
            'client_notes': client_notes,
            'administrative_note_form': administrative_note_form,
            'client_note_form': client_note_form,
        }
        return render(request, self.template_name, context)


class ClientNoteDelete(LoginRequiredNotClientMixin, View):

    def get(self, request, uuid=None):
        client_note = get_object_or_404(ClientNote, uuid=uuid)
        client_note.delete_client_note(request=request)
        return redirect('clients:client-detail', uuid=client_note.client.uuid)


class ClientEmailTemplateUpdate(LoginRequiredNotClientMixin, UpdateView):
    model = EmailTemplates
    template_name = 'clients/settings_email.html'
    form_class = ClientEmailTemplateUpdateForm
    success_url = reverse_lazy('settings-email')

    def get_object(self, queryset=None):
        return self.request.user.emailtemplates

    def get_context_data(self, **kwargs):
        context = super(ClientEmailTemplateUpdate, self).get_context_data(**kwargs)
        context['email_template'] = self.request.user.emailtemplates
        return context

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.success(self.request, 'Template saved successfully')
        ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                       verb='updated_email_template').save()
        return super().form_valid(form)


class ClientFileUploadView(LoginRequiredNotClientMixin, View):
    def post(self, request, uuid=None):
        client = get_object_or_404(Client, uuid=uuid)
        upload_form = ClientFileUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            client.check_if_user_has_permissions(Client.CAN_VIEW, self.request.user)
            file_model = upload_form.save(commit=False)
            file_model.client = client
            file_model.uploaded_by = request.user
            file_model.file_name = request.FILES['file'].name
            file_model.save()
            messages.success(self.request, 'File saved successfully')
            ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                           verb='uploaded_file', action_object=file_model.file_name, target=client.__str__()).save()
            return redirect('clients:client-detail', uuid=client.uuid)
        from django.utils.html import strip_tags
        if upload_form['file'].errors:
            messages.error(request, strip_tags(upload_form['file'].errors))
        return redirect('clients:client-detail', uuid=client.uuid)


class ClientFileDeleteView(LoginRequiredNotClientMixin, DeleteView):
    template_name = "clients/client_file_delete.html"
    model = ClientFile
    success_url = reverse_lazy('clients:client-detail')

    def get_object(self, queryset=None):
        file_object = get_object_or_404(ClientFile, uuid=self.kwargs['uuid'])
        file_object.client.check_if_user_has_permissions(
            permission=Client.CAN_DELETE, user=self.request.user)
        file_object.client.deny_permission_if_scheduler(user=self.request.user)
        return file_object

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        from django.core.files.storage import default_storage
        default_storage.delete(str(self.object.file))
        self.object.delete()
        messages.success(self.request, 'File deleted successfully')
        # logic to delete file from s3
        ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                       verb='deleted_file', action_object=self.object.file_name,
                       target=self.object.client.__str__()).save()
        return HttpResponseRedirect(success_url)


class ClientAppointmentsListView(LoginRequiredNotClientMixin, ListView):
    model = Appointment
    paginate_by = 20
    context_object_name = 'appointments'
    template_name = 'clients/client_appointments_list.html'

    def get_queryset(self):
        client = get_object_or_404(Client, uuid=self.kwargs['uuid'])
        client.check_if_user_has_permissions(Client.CAN_EDIT, self.request.user)
        appointments = Appointment.objects.select_related('assigned_to').filter(client=client).order_by(
            '-appointment_datetime_utc')
        return appointments


class ClientPortalAccessToggleView(LoginRequiredNotClientMixin, View):

    def get(self, request, uuid=None):
        client = get_object_or_404(Client, uuid=uuid)
        client.check_if_user_has_permissions(Client.CAN_EDIT, request.user)
        client.toggle_portal_access(request)
        return redirect('clients:client-detail', uuid=client.uuid)


class ClientFileDownloadView(LoginRequiredNotClientMixin, View):
    def get(self, request, uuid=None):
        file_object = get_object_or_404(ClientFile.objects, uuid=self.kwargs['uuid'])
        file_object.client.check_if_user_has_permissions(permission=Client.CAN_DELETE)
        file_object.client.deny_permission_if_scheduler(request.user)
        ActivityStream(customer=request.user.customer, actor=request.user.username,
                       verb='downloaded_file', action_object=file_object.file_name,
                       target=file_object.client).save()
        media_storage = get_storage_class()()
        return redirect(media_storage.url(file_object.file.__str__()))
