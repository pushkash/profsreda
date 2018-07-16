import json
from random import shuffle
from django.shortcuts import render, redirect
from heroes.models import ItemUser, Profile, Item
from .forms import CustomUserCreationForm, UpdateUserProfile
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template
from django.template import Context
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
            profile.grade = grade
            slots = json.dumps(
                {
                    "slot{}".format(x):
                        "img/game/avatar/" + sex + "/0{}.png".format(x) for x in range(1, 6)
                })

            profile.slots = slots
            profile.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            ctx = {
                "username": user.username,
                "site": request.META['HTTP_HOST']
            }
            subject = "Регистрация на портале Профсреда"
            to = user.email
            message_text = render_to_string('email_template.txt', ctx)
            message_html = render_to_string("email_template.html", ctx)

            # try:
            send_mail(subject, message_text, "info.profsreda@gmail.com", [to],
                      fail_silently=False, html_message=message_html)
            # except Exception as e:
            #     print(e)

            return redirect("account_profile")

        else:
            return render(request, "signup.html", {"form": form})


def profile(request):

    items = ItemUser.objects.filter(user=request.user)
    items = [i.item for i in items]
    hero_profile = Profile.objects.get(user=request.user)
    slots = json.loads(hero_profile.slots)

    if hero_profile.sex == "F":
        sex = "женский"
    elif hero_profile.sex == "M":
        sex = "мужской"
    else:
        sex = "неуказан"



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

def update_user_profile(request):
    if request.method == "GET":
        hero_profile = Profile.objects.get(user_id=request.user.id)

        form = UpdateUserProfile(initial={"grade": hero_profile.grade, "sex": hero_profile.sex})

        return render(request,
                      context=locals(),
                      template_name='update_user_profile.html')

    elif request.method == "POST":
        form = UpdateUserProfile(request.POST)
        user = User.objects.get(id=request.user.id)

        current_password = request.POST.get("current_password")

        if request.POST.get("current_password") != None:
            if user.check_password(current_password) == False:
                form.set_current_password_flag()

        if form.is_valid():
            hero_profile = Profile.objects.get(user_id=request.user.id)
            print(form.cleaned_data)
            sex = form.cleaned_data["sex"]
            grade = form.cleaned_data["grade"]
            current_password = form.cleaned_data["current_password"]
            new_password = form.cleaned_data["new_password"]
            confirm_new_password = form.cleaned_data["new_password"]

            if sex != hero_profile.sex:
                slots = json.dumps(
                    {
                        "slot{}".format(x):
                            "img/game/avatar/" + sex + "/0{}.png".format(x) for x in range(1, 6)
                    })

                hero_profile.slots = slots
                hero_profile.sex = sex

            if grade != hero_profile.grade:
                hero_profile.grade = grade

            hero_profile.save()

            if current_password and new_password and confirm_new_password:
                user.set_password(confirm_new_password)
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect("account_profile")

        else:
            return render(request, template_name="update_user_profile.html", context=locals())

