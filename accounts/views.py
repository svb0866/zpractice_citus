from accounts.forms import TeamRegisterForm, TeamMemberUpdateForm
from customers.models import ActivityStream
from .models import UserManager
from django.views import View
from django.shortcuts import render, redirect
from accounts import emailer
from zpractice_citus.custom_mixins import LoginRequiredNotClientMixin
from accounts.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from phonenumbers import parse, region_code_for_country_code
from django.contrib import messages
from guardian.shortcuts import assign_perm, get_objects_for_user


class TeamMemberSignupView(LoginRequiredNotClientMixin, View):
    template = "team/team_signup.html"

    def get(self, request):
        form = TeamRegisterForm()
        context = {'form': form}
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        form = TeamRegisterForm(request.POST or None)

        if form.is_valid():
            if not request.user.is_owner:
                raise PermissionDenied
            user_manager = UserManager()
            password = user_manager.make_random_password()

            ph = parse(form.cleaned_data['phone'])
            region_code = region_code_for_country_code(ph.country_code)

            team_member = user_manager.create_user(
                customer=request.user.customer,
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                password=password,
                is_team=True,
                is_clinician=form.cleaned_data['is_clinician'],
                is_scheduler=form.cleaned_data['is_scheduler'],
                is_biller=form.cleaned_data['is_biller'],
                region_code=region_code,
                timezone=request.user.timezone,
            )
            messages.success(request, 'Team member created successfully')
            ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                           verb='created_team_member', action_object=team_member.username).save()

            from clients.models import Client
            clients = get_objects_for_user(request.user, Client.CAN_VIEW, Client)
            for user in User.objects.filter(Q(is_owner=True) | Q(is_team=True)):
                assign_perm(Client.CAN_VIEW, user, clients)
                assign_perm(Client.CAN_EDIT, user, clients)
                assign_perm(Client.CAN_DELETE, user, clients)
                if user.is_clinician:
                    assign_perm(Client.CAN_NOTES, user, clients)

            emailer.send_team_member_credential_email(team_member, password, self.request.user)
            return redirect('team-list')
        messages.error(request, 'There was an error creating Team member')
        context = {'form': form}
        return render(request, self.template, context)


class TeamMemberUpdateView(LoginRequiredNotClientMixin, View):
    template = "team/team_update.html"

    def get(self, request, username=None, *args, **kwargs):
        user_obj = get_object_or_404(User, username=username)
        if user_obj.is_owner:
            raise PermissionDenied
        if not request.user.is_owner:
            raise PermissionDenied

        initial_values = {
            'first_name': user_obj.first_name,
            'last_name': user_obj.last_name,
            'email': user_obj.email,
            'phone': user_obj.phone,
            'is_clinician': user_obj.is_clinician,
            'is_scheduler': user_obj.is_scheduler,
            'is_biller': user_obj.is_biller,
        }
        form = TeamMemberUpdateForm(initial=initial_values, user_obj=user_obj)

        context = {'form': form}
        return render(request, self.template, context)

    def post(self, request, username=None, *args, **kwargs):
        user_obj = get_object_or_404(User, username=username)
        form = TeamMemberUpdateForm(request.POST or None, user_obj=user_obj)
        if form.is_valid():
            if user_obj.is_owner:
                raise PermissionDenied
            if not request.user.is_owner:
                raise PermissionDenied
            user_obj.first_name = form.cleaned_data['first_name']
            user_obj.last_name = form.cleaned_data['last_name']
            user_obj.email = form.cleaned_data['email']
            user_obj.phone = form.cleaned_data['phone']
            user_obj.is_clinician = form.cleaned_data['is_clinician']
            user_obj.is_scheduler = form.cleaned_data['is_scheduler']
            user_obj.is_biller = form.cleaned_data['is_biller']
            user_obj.save()
            messages.success(request, 'Team member updated successfully')
            ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                           verb='updated_team_member', action_object=user_obj.username).save()
            return redirect('team-list')
        messages.error(request, 'There was an error updating Team member')
        context = {'form': form}
        return render(request, self.template, context)


class TeamMemberDeleteView(LoginRequiredNotClientMixin, View):
    template_name = "team/team_delete.html"

    def get(self, request, username=None, *args, **kwargs):
        user_obj = get_object_or_404(User, username=username)
        if user_obj.is_owner:
            raise PermissionDenied
        if not request.user.is_owner:
            raise PermissionDenied
        context = {
            'user_obj': user_obj
        }
        return render(request, self.template_name, context)

    def post(self, request, username=None, *args, **kwargs):
        user_obj = get_object_or_404(User, username=username)
        if user_obj.is_owner:
            raise PermissionDenied
        if not request.user.is_owner:
            raise PermissionDenied
        user_obj.delete()
        messages.success(request, 'Team member deleted successfully')
        ActivityStream(customer=self.request.user.customer, actor=self.request.user.username,
                       verb='deleted_team_member', action_object=user_obj.username).save()
        return redirect('team-list')


class TeamListView(LoginRequiredNotClientMixin, View):
    def get(self, request, *args, **kwargs):
        print(User.objects.all())
        context = {
            'team_list': User.objects.filter(Q(is_owner=True) | Q(is_team=True))
        }
        return render(request, self.template_name, context)
    template_name = 'team/team_list.html'