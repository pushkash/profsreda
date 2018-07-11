from django.contrib import admin
from .models import Response, Answer, QuestionnaireResult, ResponseResult
from allauth.socialaccount.admin import SocialApp, SocialAccount, SocialToken


admin.site.unregister(SocialApp)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    pass


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionnaireResult)
class QuestionnaireResultAdmin(admin.ModelAdmin):
    pass


@admin.register(ResponseResult)
class ResponseResultAdmin(admin.ModelAdmin):
    pass
