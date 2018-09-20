import os
import uuid
import json
from PIL import Image

from random import shuffle
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string

from heroes.forms import CustomUserCreationForm, UpdateUserProfile
from heroes.models import ItemUser, Profile, ShareProfileAvatar, ProfileItem
from tests.models import ResultItem


def home(request):
    return render(request, template_name='heroes/main.html')


def custom_profile_creation(request):
    if request.method == "GET":
        form = CustomUserCreationForm()
        return render(request, "signup.html", {"form": form})

    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = email
            sex = form.cleaned_data['sex']
            grade = form.cleaned_data['grade']
            user = User.objects.create_user(username, email, form.cleaned_data['password2'])
            user.save()

            profile = Profile.objects.create(user=user)
            profile.user = user
            profile.sex = sex
            profile.grade = grade
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

            try:
                send_mail(subject, message_text, "info.profsreda@gmail.com", [to],
                          fail_silently=False, html_message=message_html)
            except BadHeaderError:
                pass
            return redirect("account_profile")
        else:
            return rBadHeaderErrorender(request, "signup.html", {"form": form})


def profile(request):
    items = ItemUser.objects.filter(user=request.user)
    items = [i.item for i in items]
    profile = Profile.objects.get(user=request.user)

    profile_items = ProfileItem.objects.filter(profile=profile)

    head = profile_items.filter(item__head_male__isnull=False).first()
    body = profile_items.filter(item__body_male__isnull=False).first()
    right_hand = profile_items.filter(item__right_hand_male__isnull=False).first()
    left_hand = profile_items.filter(item__left_hand_male__isnull=False).first()
    legs = profile_items.filter(item__legs_male__isnull=False).first()

    if profile.sex == "F":
        sex = "женский"
    elif profile.sex == "M":
        sex = "мужской"
    else:
        sex = "неуказан"

    items_results = get_content_name_result_test(items, request.user)
    return render(request, 'heroes/account.html',
                  {
                      "profile": profile,
                      "items": items,
                      "head": head,
                      "body": body,
                      "right_hand": right_hand,
                      "left_hand": left_hand,
                      "legs": legs,
                      "sex": sex
                  })


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
                if hero_profile.sex == 'F':
                    slots[x] = getattr(y, x + '_girl')
                else:
                    slots[x] = getattr(y, x)

    for i in range(1, 6):
        t = "slot{}".format(i)

        if t not in slots.keys():
            slots[t] = "img/game/avatar/" + hero_profile.sex + "/0{}.png".format(i)

    hero_profile.slots = json.dumps(slots)
    hero_profile.save()

    items_results = get_content_name_result_test(items, request.user)

    return render(request,
                  context=locals(),
                  template_name='heroes/account.html')


def profile_item(request, item_id):
    hero_profile = Profile.objects.get(user=request.user)
    try:
        hero_profile.put_item(item_id)
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

        if request.POST.get("current_password") is not None:
            if not user.check_password(current_password):
                form.set_current_password_flag()

        if form.is_valid():
            hero_profile = Profile.objects.get(user_id=request.user.id)
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
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)

            return redirect("account_profile")

        else:
            return render(request, template_name="update_user_profile.html", context=locals())


def profile_share_avatar(request):
    hero_profile = Profile.objects.get(user=request.user)
    slots = json.loads(hero_profile.slots)

    share_avatar_image, created = ShareProfileAvatar.objects.get_or_create(user_id=hero_profile.id)
    share_avatar_image.avatar_image = create_share_image(slots, share_avatar_image.avatar_image)
    share_avatar_image.save()

    return HttpResponse(share_avatar_image.avatar_image)


def update_share_image(hero_profile, slots):
    share_avatar_image, created = ShareProfileAvatar.objects.get_or_create(user_id=hero_profile.id)
    share_avatar_image.avatar_image = create_share_image(slots, share_avatar_image.avatar_image)
    share_avatar_image.save()

    return share_avatar_image.avatar_image


def get_content_name_result_test(items, user):
    items_results = {}
    for item in items:
        res_item = ResultItem.objects.filter(item=item, test_result__test_session__user=user).first()
        res_items = ResultItem.objects.filter(item=item, test_result__test_session__user=user)

        # из-за чистки бд пришлось сделать проверку, чтобы ничего не падало
        if res_item is None:
            test_id = 0
        else:
            test_id = res_item.test_result_id

        items_results[item.id] = test_id
    return items_results


def create_share_image(slots, image):
    init_avatar = Image.new('RGBA', (4267, 8534))

    init_avatar_w, init_avatar_h = init_avatar.size

    h_prev = 0

    profile_slots_ordered_array = [x[1] for x in sorted(slots.items()) if type(x[1]) != int]

    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for index, file in enumerate(profile_slots_ordered_array):

        # p = os.path.abspath(file).replace('src/img', 'src/static/img')
        p = os.path.join(project_dir + '/static', file)
        img = Image.open(p)
        w, h = img.size

        # right hand
        if index == 3:
            img_area = (init_avatar_w - w, h_prev, init_avatar_w, h + h_prev)
        else:
            img_area = (0, h_prev, w, h + h_prev)

        if index != 2:
            h_prev = h + h_prev

        init_avatar.paste(img, img_area)

    init_avatar_w, init_avatar_h = init_avatar.size

    init_avatar_w = int(init_avatar_w)
    init_avatar_h = int(init_avatar_h)

    init_avatar = init_avatar.resize((init_avatar_w, init_avatar_h), Image.ANTIALIAS)

    init_avatar = init_avatar.resize((int(init_avatar_w / 14), int(init_avatar_h / 14)), Image.ANTIALIAS)

    blanc_img = Image.new('RGBA', (1300, 607))  # 1480

    b_w, b_h = blanc_img.size
    w, h = init_avatar.size

    blanc_img.paste(init_avatar, (int((b_w - w) / 2), 0, int((b_w + w) / 2), h))

    # Создание рамки у изображения
    # blanc_img = ImageOps.expand(blanc_img, border = 1, fill ='black')

    image_name = str(uuid.uuid4()).replace('-', '') + '.png'

    share_img_path = os.path.join(project_dir, "static/img/share_avatars")

    if not os.path.isdir(share_img_path):
        os.mkdir(share_img_path)

    blanc_img.save(share_img_path + '/' + image_name)

    if image is not None:
        try:
            remove_prev_profile_share_avatar(share_img_path + '/' + image)
        except Exception as e:
            pass

    return image_name


def remove_prev_profile_share_avatar(file):
    os.remove(file)
