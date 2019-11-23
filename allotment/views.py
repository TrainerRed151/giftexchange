from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect

from allotment.models import Participant, Party


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


@login_required
def party_view(request):
    party = Party.objects.get(credentials=request.user)
    participants = Participant.objects.filter(party=party)
    ctx = {
        'participants': participants,
        'party_name': party.credentials.username,
    }

    return render(request, 'party.html', ctx)
