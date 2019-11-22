from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect

from allotment.models import Party


def home(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            return redirect('login')
        elif 'signup' in request.POST:
            return redirect('signup')
    return render(request, 'home.html', {})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            Party.objects.create(credentials=user)
            login(request, user)
            return redirect('party_view')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def party_view(request):
    return HttpResponse('Party view')
