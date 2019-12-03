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
        'decrypt_url': reverse('decrypt'),
        'encrypt_url': reverse('encrypt'),
        'gen_key_url': reverse('public_key'),
        'participants': participant_tuples,
        'party_name': party.credentials.username,
    }

    return render(request, 'party.html', ctx)


@login_required
def public_key_create(request):
    empty_hash_key = 'BzSKPETSwTq4hrPHLrNwDQvutqrZjkXPXEPFJyxPpCMJ/7APcr4LnGUq8PkrscSSmwZutr9oxAqkLFRis5u4FexNp'

    ctx = {
        'invalid': False,
        'confirm_error': False,
    }

    if request.method == 'POST':
        public_key = request.POST['submit']
        if '!' in public_key:
            ctx['confirm_error'] = True
        elif public_key in ('', '1/1', empty_hash_key):
            ctx['invalid'] = True
        else:
            x58, y58 = public_key.split('/')
            xb = base58.b58decode(x58.encode())
            yb = base58.b58decode(y58.encode())
            public_key_binary = xb + yb

            party = Party.objects.get(credentials=request.user)
            Participant.objects.get_or_create(party=party, public_key=public_key_binary)

            return redirect('party_view')

    return render(request, 'public_key.html', ctx)


@login_required
def encrypt_message(request):
    x_list = []
    y_list = []
    id_list = []
    p = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F', 16)
    for participant in Participant.objects.filter(party__credentials=request.user).order_by('public_key'):
        x = int.from_bytes(participant.public_key[:32], 'big')
        z = ((x * x * x) + 7) % p
        y = pow(z, (p + 1) // 4, p)
        x_hex = hex(x)[2:]
        y_hex = hex(y)[2:]
        x_list.append(x_hex)
        y_list.append(y_hex)
        id_list.append(participant.id)

    ctx = {
        'bad_passwd': False,
        'empty_msg': False,
        'id_list': id_list,
        'x_list': x_list,
        'y_list': y_list,
    }

    if request.method == 'POST':
        cipher, gifter_id_str = request.POST['cipher'].split('/')
        if cipher == '!':
            ctx['bad_passwd'] = True
        elif cipher == '?':
            ctx['empty_msg'] = True
        else:
            gifter_id = int(gifter_id_str)
            #cipher_int = int(cipher, 16)
            #cipher_58 = base58.b58encode_int(cipher_int)
            #gifter_obj = Participant.objects.get(id=gifter_id)
            #gifter_obj.recipient_cipher = cipher_58.decode()
            gifter_obj = Participant.objects.get(id=gifter_id)
            gifter_obj.recipient_cipher = cipher
            gifter_obj.save()

            return redirect('party_view')

    return render(request, 'encrypt.html', ctx)


@login_required
def decrypt_message(request):
    x_list = []
    y_list = []
    cipher_list = []
    p = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F', 16)
    for participant in Participant.objects.filter(party__credentials=request.user).order_by('public_key'):
        x = int.from_bytes(participant.public_key[:32], 'big')
        z = ((x * x * x) + 7) % p
        y = pow(z, (p + 1) // 4, p)
        x_hex = hex(x)[2:]
        y_hex = hex(y)[2:]
        x_list.append(x_hex)
        y_list.append(y_hex)
        #cipher = hex(base58.b58decode_int(participant.recipient_cipher.encode()))[2:]
        #cipher_list.append(cipher)
        cipher_list.append(participant.recipient_cipher)

    ctx = {
        'bad_passwd': False,
        'cipher_list': cipher_list,
        'empty_msg': False,
        'x_list': x_list,
        'y_list': y_list,
    }

    if request.method == 'POST':
        error = request.POST['error']
        if error == '!':
            ctx['bad_passwd'] = True
        elif error == '?':
            ctx['empty_msg'] = True

    return render(request, 'decrypt.html', ctx)
