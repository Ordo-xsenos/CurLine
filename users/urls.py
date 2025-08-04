from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import login,registration,get_discord_members
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html", success_url="articles:home"), name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", registration, name="register"),
    path('discord/members/', get_discord_members, name='discord_members'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
]


