"""zpractice_citus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path, include
from accounts.views import TeamMemberSignupView, TeamMemberUpdateView, TeamMemberDeleteView, TeamListView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import handler404, handler500
from clients.views import ClientEmailTemplateUpdate
from customers.views import HomepageView, SignUpView
urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('', HomepageView.as_view(), name='homepage'),
    #path('', auth_views.LoginView.as_view(redirect_authenticated_user=True)),
    path('accounts/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('team/', TeamListView.as_view(), name='team-list'),
    path('team/create/', TeamMemberSignupView.as_view(), name='team-create'),
    path('team/<str:username>/update/', TeamMemberUpdateView.as_view(), name='team-update'),
    path('team/<str:username>/delete/', TeamMemberDeleteView.as_view(), name='team-delete'),

    path('clients/', include('clients.urls')),
    path('appointments/', include('appointments.urls')),

    path('settings/email/', ClientEmailTemplateUpdate.as_view(), name='settings-email'),
]
handler404 = handler404
handler500 = handler500

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
