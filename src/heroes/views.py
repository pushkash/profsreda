import json
from random import shuffle
from django.shortcuts import render, redirect
from heroes.models import ItemUser, Profile, Item
from .forms import CustomUserCreationForm
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import random

def home(request):
    return render(request, template_name='heroes/main.html')


def customProfileCreation(request):

    if request.method == "GET":
        form = CustomUserCreationForm()
        return render(request, "signup.html", {"form": form})

    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = email.split('@')[0]
            sex = form.cleaned_data['sex']
            grade = form.cleaned_data['grade']

            user = User.objects.create_user(username, email, form.cleaned_data['password2'])
            user.save()

            profile = Profile.objects.create(user=user)
            profile.user = user
            profile.sex = sex
            slots = json.dumps(
                {
                    "slot{}".format(x):
                        "img/game/avatar/" + sex + "/0{}.png".format(x) for x in range(1, 6)
                })

            profile.slots = slots
            profile.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect("account_profile")

        else:
            return HttpResponse(500)


def profile(request):

    items = ItemUser.objects.filter(user=request.user)
    items = [i.item for i in items]
    hero_profile = Profile.objects.get(user=request.user)
    slots = json.loads(hero_profile.slots)

    return render(request,
                  context=locals(),
                  template_name='heroes/account.html')


def profile_random(request):
    items = ItemUser.objects.filter(user=request.user)
    items = [i.item for i in items]

    hero_profile = Profile.objects.get(user=request.user)

    r_items = items
    shuffle(r_items)

    slots = {}

    for item in r_items:
        to_write = []
        available = []

        if item.slot1 != '':
            to_write.append(item)
            if 'slot1' not in slots.keys():
                available.append('slot1')

        if item.slot2 != '':
            to_write.append(item)
            if 'slot2' not in slots.keys():
                available.append('slot2')

        if item.slot3 != '':
            to_write.append(item)
            if 'slot3' not in slots.keys():
                available.append('slot3')

        if item.slot4 != '':
            to_write.append(item)
            if 'slot4' not in slots.keys():
                available.append('slot4')

        if item.slot5 != '':
            to_write.append(item)
            if 'slot5' not in slots.keys():
                available.append('slot5')

        if len(to_write) == len(available):
            for x, y in zip(available, to_write):
                slots["{}_pk".format(x)] = y.pk
                slots[x] = getattr(y, x)

    for i in range(1,6):
        t = "slot{}".format(i)

        if t not in slots.keys():
            slots[t] = "img/game/avatar/" + hero_profile.sex +"/0{}.png".format(i)

    hero_profile.slots = json.dumps(slots)
    hero_profile.save()

    return render(request,
                  context=locals(),
                  template_name='heroes/account.html')


def profile_item(request, item_pk):
    hero_profile = Profile.objects.get(user=request.user)
    try:
        hero_profile.put_item(item_pk)
        print('Success')
        return profile(request)

    except Exception as e:
        print(e.args[0])
        return profile(request)
