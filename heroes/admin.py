from django.contrib import admin
from heroes.models import Item, ItemUser, Profile


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemUser)
class ItemUserAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile)
