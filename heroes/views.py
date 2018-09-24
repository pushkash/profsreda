import os
import uuid
import random
from PIL import Image

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string

from profsreda.settings import BASE_DIR

from heroes.forms import CustomUserCreationForm, UpdateUserProfile
from heroes.models import ItemUser, Profile, ShareProfileAvatar
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

            user_profile = Profile.objects.create(user=user)
            user_profile.user = user
            user_profile.sex = sex
            user_profile.grade = grade
            user_profile.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            ctx = {
                "username": user.username,
                "site": request.META['HTTP_HOST']
            }
            subject = "Регистрация на портале Профсреда"
            to = user.email
            message_text = render_to_string('email_template.txt', ctx)
            message_html = render_to_string("email_template.html", ctx)

            send_mail(subject, message_text, "info.profsreda@gmail.com", [to],
                      fail_silently=False, html_message=message_html)
            return redirect("account_profile")
        else:
            return render(request, "signup.html", {"form": form})


def profile(request):
    items = ItemUser.objects.filter(user=request.user)
    items = [i.item for i in items]
    user_profile = Profile.objects.get(user=request.user)

    head, body, right_hand, left_hand, legs = user_profile.get_items_urls()

    items_results = get_content_name_result_test(items, request.user)
    return render(request, 'heroes/profile.html', locals())


def profile_random(request):
    items = [item_user.item for item_user in ItemUser.objects.filter(user=request.user)]
    random.shuffle(items)

    random_items_amount = random.randint(0, len(items))
    for _ in range(random_items_amount):
        item_to_put_on = random.choice(items)
        items.remove(item_to_put_on)
        Profile.objects.get(user=request.user).put_item(item_to_put_on.id)

    return redirect(profile)


def profile_item(request, item_id):
    user_profile = Profile.objects.get(user=request.user)
    try:
        user_profile.put_item(item_id)
        return profile(request)
    except Exception as e:
        return profile(request)


def update_user_profile(request):
    if request.method == "GET":
        user_profile = Profile.objects.get(user_id=request.user.id)

        form = UpdateUserProfile(initial={"grade": user_profile.grade, "sex": user_profile.sex})

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
            user_profile = Profile.objects.get(user_id=request.user.id)
            sex = form.cleaned_data["sex"]
            grade = form.cleaned_data["grade"]
            current_password = form.cleaned_data["current_password"]
            new_password = form.cleaned_data["new_password"]
            confirm_new_password = form.cleaned_data["new_password"]

            if sex != user_profile.sex:
                user_profile.sex = sex
            if grade != user_profile.grade:
                user_profile.grade = grade
            user_profile.save()

            if current_password and new_password and confirm_new_password:
                user.set_password(confirm_new_password)
                user.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)

            return redirect("account_profile")
        else:
            return render(request, template_name="update_user_profile.html", context=locals())


def profile_share_avatar(request):
    user_profile = Profile.objects.get(user=request.user)
    head, body, right_hand, left_hand, legs = user_profile.get_items_urls()

    return HttpResponse(update_share_image(user_profile,
                                           [head, body, right_hand, left_hand, legs]))


def update_share_image(user_profile, items):
    share_avatar_image, created = ShareProfileAvatar.objects.get_or_create(user_id=user_profile.id)
    share_avatar_image.avatar_image = create_share_image(items, share_avatar_image.avatar_image)
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


def create_share_image(items, image):
    init_avatar = Image.new('RGBA', (4267, 8534))
    init_avatar_w, init_avatar_h = init_avatar.size
    h_prev = 0

    for index, file_path in enumerate(items):
        img = Image.open(file_path)
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

    share_img_path = os.path.join(BASE_DIR, "/media/img/share_avatars")

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
