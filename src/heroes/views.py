import json
from random import shuffle
from django.shortcuts import render
from heroes.models import ItemUser, Profile, Item


def home(request):
    return render(request, template_name='heroes/main.html')


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
            slots[t] = "img/game/avatar/M/0{}.png".format(i)

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
