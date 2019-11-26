import base58

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

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
    participant_tuples = []
    participants = Participant.objects.filter(party=party)

    for participant in participants:
        public_key = base58.b58encode(participant.public_key[:32]).decode()
        participant_tuples.append((public_key, participant.recipient_cipher))
    ctx = {
        'gen_key_url': reverse('public_key'),
        'participants': participant_tuples,
        'party_name': party.credentials.username,
    }

    return render(request, 'party.html', ctx)


@login_required
def public_key_create(request):
    empty_hash_key = 'BzSKPETSwTq4hrPHLrNwDQvutqrZjkXPXEPFJyxPpCMJ/7APcr4LnGUq8PkrscSSmwZutr9oxAqkLFRis5u4FexNp'

    ctx = {'invalid': False}
    if request.method == 'POST':
        public_key = request.POST['submit']
        if public_key in ('', '1/1', empty_hash_key):
            ctx['invalid'] = True
        else:
            x58, y58 = public_key.split('/')
            xb = base58.b58decode(x58.encode())
            yb = base58.b58decode(x58.encode())
            public_key_binary = xb + yb

            party = Party.objects.get(credentials=request.user)
            Participant.objects.get_or_create(party=party, public_key=public_key_binary)

            return redirect('party_view')

    return render(request, 'public_key.html', ctx)
