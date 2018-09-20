import json

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Profile(models.Model):
    SEX = [
        ("M", "Мужской"),
        ("F", "Женский")
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
    grade = models.CharField(
        max_length=2,
        null=True,
        blank=True
    )
    sex = models.CharField(
        max_length=1,
        choices=SEX,
        null=True,
        blank=True
    )

    # slots = models.TextField(
    #     null=False,
    #     default=json.dumps(
    #         {
    #             "slot{}".format(x):
    #                 "img/game/avatar/M/0{}.png".format(x) for x in range(1, 6)
    #         }
    #     )
    # )

    def put_item(self, item_id):
        pass
        # item = Item.objects.get(id=item_id)
        # profile_items = ProfileItem.objects.get(profile=self)
        #
        # # Remove item from profile if it was putted on
        # for profile_item in profile_items:
        #     if profile_item.item == item:
        #         profile_item.delete()
        #         return
        # else:
        #     for profile_item in profile_items:
        #         if profile_item.item.head_male is not None and item.head_male is not None or \
        #                 profile_item.item.body_male is not None and item.body_male is not None or \
        #                 profile_item.item.left_hand_male is not None and item.left_hand_male is not None or \
        #                 profile_item.item.right_hand_male is not None and item.right_hand_male is not None or \
        #                 profile_item.item.legs_male is not None and item.legs.male is not None:
        #             profile_item.delete()
        #     ProfileItem.objects.create(profile=self,
        #                                item=item)


class Item(models.Model):
    name = models.CharField(max_length=100)
    icon = models.FileField(
        blank=True,
        upload_to="item_image/",
        verbose_name=_("Изображение"),
        help_text=_("Изображение предмета надетого на")
    )
    slot3 = models.FileField(
        blank=True,
        upload_to="item_image/",
        verbose_name=_("Изображение"),
        help_text=_("Изображение предмета надетого на")
    )
    slot4 = models.FileField(
        blank=True,
        upload_to="item_image/",
        verbose_name=_("Изображение"),
        help_text=_("Изображение предмета надетого на")
    )
    slot5 = models.FileField(
        blank=True,
        upload_to="item_image/",
        verbose_name=_("Изображение"),
        help_text=_("Изображение предмета надетого на")
    )
    slot1_girl = models.FileField(
        blank=True,
        upload_to="item_image/",
        verbose_name=_("Изображение"),
        help_text=_("Изображение предмета надетого на")
    )
    slot2_girl = models.FileField(
        blank=True,
        upload_to="item_image/",
        verbose_name=_("Изображение"),
        help_text=_("Изображение предмета надетого на")
    )
    slot3_girl = models.FileField(
        blank=True,
        upload_to="item_image/",
        verbose_name=_("Изображение"),
        help_text=_("Изображение предмета надетого на")
    )
    slot4_girl = models.FileField(
        blank=True,
        upload_to="item_image/",
        verbose_name=_("Изображение"),
        help_text=_("Изображение предмета надетого на")
    )
    slot5_girl = models.FileField(
        blank=True,
        upload_to="item_image/",
        verbose_name=_("Изображение"),
        help_text=_("Изображение предмета надетого на")
    )
    category = models.ForeignKey(
        "tests.Category",
        on_delete=models.CASCADE,
        verbose_name=_("Категория"),
        help_text=_("Категория, за получение которой даётся награда")
    )

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return self.name

    def main_dict(self):
        """
        Returns main info about Item
        :return: dict with main info about Item
        """
        item = {
            "id": self.id,
            "name": self.name,
            "icon": self.icon.url
        }
        return item


class ProfileItem(models.Model):
    profile = models.ForeignKey(
        "heroes.Profile",
        verbose_name=_("Профиль"),
        help_text=_("Профиль пользователя, надевшего предмет"),
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        "heroes.Item",
        verbose_name=_("Предмет"),
        help_text=_("Предмет, который надел пользователь"),
        on_delete=models.CASCADE
    )


class ItemUser(models.Model):
    item = models.ForeignKey(
        "heroes.Item",
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


class ShareProfileAvatar(models.Model):
    user_id = models.PositiveIntegerField(
        null=False,
        unique=True
    )
    avatar_image = models.TextField(
        default=""
    )
