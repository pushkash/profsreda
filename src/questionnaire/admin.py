from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Question, Questionnaire, Category
from .models import AnswerChoice, AnswerType

from django.contrib.auth.models import Group
from django.contrib.auth.models import User

admin.site.unregister(Group)
admin.site.unregister(User)

admin.site.site_header = 'Профсреда: портал профориентации'
admin.site.site_title = 'Профсреда: портал профориентации'
admin.site.index_title = 'Административная Панель'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


class QuestionInline(admin.StackedInline):
    model = Question


class CategoryInline(admin.StackedInline):
    model = Category


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    inlines = (QuestionInline,)


class AnswerChoiceInline(admin.StackedInline):
    model = AnswerChoice


@admin.register(AnswerType)
class AnswerTypeAdmin(admin.ModelAdmin):
    inlines = (AnswerChoiceInline, )


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
