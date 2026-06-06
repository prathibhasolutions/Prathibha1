from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import NoReverseMatch, reverse
from django.shortcuts import redirect, render


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def continue_with_google(request):
    try:
        return redirect(reverse('socialaccount_login', kwargs={'provider': 'google'}))
    except NoReverseMatch:
        messages.info(request, 'Google login is not configured yet. Please use username/password login for now.')
        return redirect('login')
