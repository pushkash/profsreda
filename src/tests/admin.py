from django.contrib import admin

from .models import *


admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Category)
admin.site.register(AnswerCategory)

admin.site.register(TestSession)
admin.site.register(Answer)
