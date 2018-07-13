import json

from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import status

from .models import Questionnaire


class QuestionnaireListView(LoginRequiredMixin, ListView):
    context_object_name = 'questionaries_list'
    queryset = Questionnaire.objects.all()
    template_name = 'responses/tests.html'


def get_questionnaire(request, questionnaire_id):
    """
    Возвращает данные всего опросника
    :param request: http request
    :param questionnaire_id: id опросника, по которому нужно получить данные
    :return: http response c JSON объектом опросника
    """
    try:
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
        questionnaire_data = questionnaire.dict()
        return HttpResponse(
            status=status.HTTP_200_OK,
            content=json.dumps({"questionnaire": questionnaire_data}),
            content_type="application/json"
        )
    except Questionnaire.DoesNotExist:
        return HttpResponse(
            status=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"Ошибка": "Опросника с таким id не существует"}),
            content_type="application/json"
        )
