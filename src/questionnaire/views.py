from django.shortcuts import render
from .models import Questionnaire
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin


class QuestionnaireListView(LoginRequiredMixin, ListView):
    context_object_name = 'questionaries_list'
    queryset = Questionnaire.objects.all()
    template_name = 'responses/tests.html'
