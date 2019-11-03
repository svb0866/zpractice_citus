from django.shortcuts import render, redirect
from django.views import View
from customers.models import Customer, ActivityStream
from customers.forms import RegisterForm
from django.conf import settings
from accounts.models import UserManager
from phonenumbers import parse, region_code_for_country_code
from uuid import uuid4


class SignUpView(View):
    template = "signup.html"

    def get(self, request):
        form = RegisterForm()
        context = {'form': form}
        return render(request, self.template, context)

    def post(self, request):
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            formdata = form.cleaned_data.copy()
            formdata.pop('password2')
            formdata.pop('password')
            tenant = Customer()
            tenant.username = form.cleaned_data['username']
            tenant.first_name = form.cleaned_data['first_name']
            tenant.last_name = form.cleaned_data['last_name']
            tenant.email = form.cleaned_data['email']
            tenant.phone = form.cleaned_data['phone']
            tenant.timezone = form.cleaned_data['timezone']
            ph = parse(form.cleaned_data['phone'])
            region_code = region_code_for_country_code(ph.country_code)
            tenant.region_code = region_code
            tenant.save()
            print(tenant.__dict__)

            user_manager = UserManager()
            user_manager.create_user(customer=tenant,
                                     username=form.cleaned_data['username'],
                                     email=form.cleaned_data['email'],
                                     password=form.cleaned_data['password'],
                                     first_name=form.cleaned_data['first_name'],
                                     last_name=form.cleaned_data['last_name'],
                                     phone=form.cleaned_data['phone'],
                                     is_owner=True,
                                     is_clinician=True,
                                     is_scheduler=True,
                                     is_biller=True,
                                     region_code=tenant.region_code,
                                     timezone=tenant.timezone,
                                     )
            ActivityStream(customer=tenant, actor=form.cleaned_data['username'],
                           verb='signed up').save()
            return redirect('login') # to be changed later
        context = {'form': form}
        return render(request, self.template, context)


class HomepageView(View):
    template_name = 'homepage.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
