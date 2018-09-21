from django.contrib import admin

from .models import *


admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Category)
admin.site.register(Answer)

admin.site.register(TestSession)
admin.site.register(TestResult)
admin.site.register(Response)
admin.site.register(ResultItem)
admin.site.register(ResultCategory)
admin.site.register(TestGradeInterval)
admin.site.register(AnswerCategory)
