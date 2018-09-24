import os

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from profsreda.settings import BASE_DIR


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

    def put_item(self, item_id):
        item = Item.objects.get(id=item_id)
        profile_items = ProfileItem.objects.filter(profile=self)

        # Remove item from profile if it was putted on
        for profile_item in profile_items:
            if profile_item.item == item:
                profile_item.delete()
                return
        else:
            for profile_item in profile_items:
                if profile_item.item.head_male != "" and item.head_male != "" or \
                        profile_item.item.body_male != "" and item.body_male != "" or \
                        profile_item.item.left_hand_male != "" and item.left_hand_male != "" or \
                        profile_item.item.right_hand_male != "" and item.right_hand_male != "" or \
                        profile_item.item.legs_male != "" and item.legs_male != "":
                    profile_item.delete()
            ProfileItem.objects.create(profile=self,
                                       item=item)

    def get_putted_on_items_images(self):
        profile_items = ProfileItem.objects.filter(profile=self)
        head = profile_items.exclude(item__head_male="").first()
        body = profile_items.exclude(item__body_male="").first()
        right_hand = profile_items.exclude(item__right_hand_male="").first()
        left_hand = profile_items.exclude(item__left_hand_male="").first()
        legs = profile_items.exclude(item__legs_male="").first()

        if self.sex == "M":
            head = head.item.head_male.url if head is not None else None
            body = body.item.body_male.url if body is not None else None
            right_hand = right_hand.item.right_hand_male.url if right_hand is not None else None
            left_hand = left_hand.item.left_hand_male.url if left_hand is not None else None
            legs = legs.item.legs_male.url if legs is not None else None
        else:
            head = head.item.head_female.url if head is not None else None
            body = body.item.body_female.url if body is not None else None
            right_hand = right_hand.item.right_hand_female.url if right_hand is not None else None
            left_hand = left_hand.item.left_hand_female.url if left_hand is not None else None
            legs = legs.item.legs_female.url if legs is not None else None

        return head, body, right_hand, left_hand, legs

    def get_items_urls(self):
        head, body, right_hand, left_hand, legs = self.get_putted_on_items_images()

        print(self.sex)

        head = "/media/img/game/avatar/{}/01.png".format(self.sex) if head is None \
            else head
        print(self.sex)
        body = "/media/img/game/avatar/{}/02.png".format(self.sex) if body is None \
            else body
        print(self.sex)
        right_hand = "/media/img/game/avatar/{}/03.png".format(self.sex) if right_hand is None \
            else right_hand
        print(self.sex)
        left_hand = "/media/img/game/avatar/{}/04.png".format(self.sex) if left_hand is None \
            else left_hand
        print(self.sex)
        legs = "/media/img/game/avatar/{}/05.png".format(self.sex) if legs is None \
            else legs
        print(self.sex)

        print(head, body, right_hand, left_hand, legs)

        return head, body, right_hand, left_hand, legs


class Item(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(
        upload_to="item_image/",
        verbose_name=_("Изображение предмета"),
        help_text=_("Изображение предмета")
    )
    head_male = models.ImageField(
        blank=True,
        null=True,
        upload_to="item_image/",
        verbose_name=_("Изображение гловы [мужской аватар]"),
        help_text=_("Изображение предмета надетого на голову")
    )
    body_male = models.ImageField(
        blank=True,
        null=True,
        upload_to="item_image/",
        verbose_name=_("Изображение туловища [мужской аватар]"),
        help_text=_("Изображение предмета надетого на туловище")
    )
    right_hand_male = models.ImageField(
        blank=True,
        null=True,
        upload_to="item_image/",
        verbose_name=_("Изображение правой руки [мужской аватар]"),
        help_text=_("Изображение предмета надетого на правую руку")
    )
    left_hand_male = models.ImageField(
        blank=True,
        null=True,
        upload_to="item_image/",
        verbose_name=_("Изображение левой руки [мужской аватар]"),
        help_text=_("Изображение предмета надетого на левую руку")
    )
    legs_male = models.ImageField(
        blank=True,
        null=True,
        upload_to="item_image/",
        verbose_name=_("Изображение ног [мужской аватар]"),
        help_text=_("Изображение предмета надетого на ноги")
    )
    head_female = models.ImageField(
        blank=True,
        null=True,
        upload_to="item_image/",
        verbose_name=_("Изображение гловы [женский аватар]"),
        help_text=_("Изображение предмета надетого на голову")
    )
    body_female = models.ImageField(
        blank=True,
        null=True,
        upload_to="item_image/",
        verbose_name=_("Изображение туловища [женский аватар]"),
        help_text=_("Изображение предмета надетого на туловище")
    )
    right_hand_female = models.ImageField(
        blank=True,
        null=True,
        upload_to="item_image/",
        verbose_name=_("Изображение правой руки [женский аватар]"),
        help_text=_("Изображение предмета надетого на правую руку")
    )
    left_hand_female = models.ImageField(
        blank=True,
        null=True,
        upload_to="item_image/",
        verbose_name=_("Изображение левой руки [женский аватар]"),
        help_text=_("Изображение предмета надетого на левую руку")
    )
    legs_female = models.ImageField(
        blank=True,
        null=True,
        upload_to="item_image/",
        verbose_name=_("Изображение ног [женский аватар]"),
        help_text=_("Изображение предмета надетого на ноги ")
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
