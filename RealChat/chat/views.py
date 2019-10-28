from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Message


# Create your views here.
def index(request):
    return render(request, 'index.html')


@login_required
def room(request, room_name):
    return render(request, 'chat.html',
                  {
                      'room_name_json': mark_safe(json.dumps(room_name)),
                      'username': mark_safe(json.dumps(request.user.username))
                  })


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chat')
        else:
            messages.error(request, 'invalid credentials')
            return redirect('login')

    else:
        return render(request, 'login.html')


@login_required
def chat(request):
    contacts = set()
    frm = request.user.id
    for i in Message.objects.raw('select id,to_id from chat_message where author_id = %s' % frm):
        contacts.add(i.to_id)
    for i in Message.objects.raw('select id,author_id from chat_message where to_id=%s' %frm):
        contacts.add(i.author_id)
    rooms = room_selector(frm, contacts)
    return render(request, 'chat.html',
                  {
                      'room_name_json': mark_safe(
                          json.dumps(str(User.objects.get(username=request.user.username).pk).zfill(5))),
                      'username': mark_safe(json.dumps(request.user.username)),
                      'contacts': mark_safe(json.dumps(rooms))
                  })


def search(request):
    contacts = set()
    rooms = {}
    if User.objects.filter(username=request.GET['usr']).exists():
        frm = request.user.id
        to = User.objects.get(username=request.GET['usr']).pk
        if frm > to:
            res = str(to).zfill(5) + str(frm).zfill(5)
        else:
            res = str(frm).zfill(5) + str(to).zfill(5)
        rooms[User.objects.get(id=to).username] = res
        a = rooms
        for i in Message.objects.raw('select id,to_id from chat_message where author_id = %s' % request.user.id):
            contacts.add(i.to_id)
        rooms = room_selector(frm, contacts)
        room = rooms.update(a)

    return render(request, 'chat.html',
                  {
                      'room_name_json': mark_safe(json.dumps(User.objects.get(username=request.user.username).pk)),
                      'username': mark_safe(json.dumps(request.user.username)),
                      'contacts': mark_safe(json.dumps(rooms)),
                  })


def room_selector(frm, contacts):
    rooms = {}
    for to in contacts:
        if frm > to:
            res = str(to).zfill(5) + str(frm).zfill(5)
        else:
            res = str(frm).zfill(5) + str(to).zfill(5)
        rooms[User.objects.get(id=to).username] = res
    return rooms


def uploadpic(request):
    if request.method == 'POST':
        pic = request.POST['pic']

    else:
        return render(request,'uploadpic.html')


def register(request):
    if request.method == 'POST':
        first = request.POST['first']
        last = request.POST['last']
        username = request.POST['username']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']
        email = request.POST['email']
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username taken')
            return redirect('register')
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists, try login')
            return redirect('register')
        else:
            user = User.objects.create_user(username=username, password=pass1, email=email, first_name=first,
                                            last_name=last)
            user.save()

            return redirect('login')
    else:
        return render(request, 'registration.html')


def logout(request):
    auth.logout(request)
    return redirect('login')
