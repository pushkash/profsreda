from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from questionnaire_responses.models import QuestionnaireResult
import json


class Profile(models.Model):
    SEX = [
        ("М", "Мужской"),
        ("Ж", "Женский")
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(
        max_length=400,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        max_length=400,
        null=True,
        blank=True
    )
    father_name = models.CharField(
        max_length=400,
        null=True,
        blank=True
    )
    birth_date = models.DateField(
        null=True,
        blank=True
    )
    sex = models.CharField(
        max_length=1,
        choices=SEX,
        null=True,
        blank=True
    )

    slots = models.TextField(
        null=False,
        default=json.dumps(
            {
                "slot{}".format(x):
                    "img/game/avatar/M/0{}.png".format(x) for x in range(1,6)
            }
        )
    )

    def put_item(self, item_pk):
        item = Item.objects.get(pk=item_pk)
        available_items = ItemUser.objects.filter(user=self.user)
        if available_items.count() < 1:
            raise Exception('No available items!')
        available_items = [i.item for i in available_items]
        if item not in available_items:
            raise Exception('Item is not available!')

        slots = json.loads(self.slots)

        to_write = {}
        to_clean = set()

        if item.slot1 != '':
            to_write['slot1'] = item
            if 'slot1_pk' in slots.keys():
                to_clean.add(slots['slot1_pk'])

        if item.slot2 != '':
            to_write['slot2'] = item
            if 'slot2_pk' in slots.keys():
                to_clean.add(slots['slot2_pk'])

        if item.slot3 != '':
            to_write['slot3'] = item
            if 'slot3_pk' in slots.keys():
                to_clean.add(slots['slot3_pk'])

        if item.slot4 != '':
            to_write['slot4'] = item
            if 'slot4_pk' in slots.keys():
                to_clean.add(slots['slot4_pk'])

        if item.slot5 != '':
            to_write['slot5'] = item
            if 'slot5_pk' in slots.keys():
                to_clean.add(slots['slot5_pk'])

        for k in to_write.keys():
            slots["{}_pk".format(k)] = to_write[k].pk
            slots[k] = getattr(to_write[k], k)

        for i in range(1, 6):
            s = "slot{}".format(i)
            s_pk = "{}_pk".format(s)
            if s_pk in slots.keys():
                if slots[s_pk] in to_clean:
                    slots[s] = "img/game/avatar/M/0{}.png".format(i)
                    del slots[s_pk]

        self.slots = json.dumps(slots)
        self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Item(models.Model):
    name = models.CharField(max_length=100)
    icon = models.TextField()
    variant = models.ForeignKey(
        QuestionnaireResult,
        on_delete=models.PROTECT,
        null=True
    )
    slot1 = models.TextField(default="", blank=True)
    slot2 = models.TextField(default="", blank=True)
    slot3 = models.TextField(default="", blank=True)
    slot4 = models.TextField(default="", blank=True)
    slot5 = models.TextField(default="", blank=True)

    slot1_girl = models.TextField(default="", blank=True)
    slot2_girl = models.TextField(default="", blank=True)
    slot3_girl = models.TextField(default="", blank=True)
    slot4_girl = models.TextField(default="", blank=True)
    slot5_girl = models.TextField(default="", blank=True)

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return self.name


class ItemUser(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    class Meta:
        unique_together = (('user', 'item'),)
        verbose_name = 'Предмет у пользователя'
        verbose_name_plural = 'Предметы у пользователей'

    def __str__(self):
        return "{} -> {}".format(self.item.name, self.user.email or self.user.username)