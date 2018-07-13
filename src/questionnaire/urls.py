from django.urls import path

from . import views

urlpatterns = [
    path(r"get_questionnaire/<int:questionnaire_id>", views.get_questionnaire)
]
