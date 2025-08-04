from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import auth, messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
#from articles.models import Subcategory
from .forms import UserLoginForm, UserRegistrationForm,UserEditForm
import requests
from django.http import JsonResponse
from django.conf import settings


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('articles:home'))
    else:
        form = UserLoginForm()
    #subcategories = Subcategory.objects.all()
    context = {'form': form,}
    return render(request, 'login.html', context)


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = UserRegistrationForm()
    from .forms import UserLoginForm  # импортируем здесь, чтобы избежать циклов
    auth_form = UserLoginForm()
    context = {'form': form, 'auth_form': auth_form}
    return render(request, 'registration.html', context)


# @login_required
# def profile(request):
#     if request.method == 'POST':
#         user_form = UserEditForm(request.POST, instance=request.user)
#         profile_form = UserProfileForm(request.POST, instance=request.user.profile)
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             return HttpResponseRedirect(reverse('users:profile'))
#         else:
#             messages.error(request, f'{user_form.errors} & {profile_form.errors}')
#     else:
#         user_form = UserEditForm(instance=request.user)
#         profile_form = UserProfileForm(instance=request.user.profile)
#     context = {
#         'title': 'Store - Профиль',
#         'user_form': user_form,
#         'profile_form': profile_form
#     }
#     return render(request, 'profile1.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('articles:home'))


SERVER_ID = "1348586284104290344"

def get_discord_members(request):
    url = f"https://discord.com/api/guilds/{SERVER_ID}/widget.json"
    try:
        response = requests.get(url)
        data = response.json()
        return JsonResponse({"members": data.get("presence_count", 0)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
