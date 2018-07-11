from django import forms
import random

from heroes.models import Item, ItemUser
from .models import Response, Answer, QuestionnaireResult
from .forms import ResponseForm, AnswerForm
from django.shortcuts import render
from .models import Questionnaire
from .result_processor import result_processor
from questionnaire.models import AnswerChoice
from django.contrib.auth.decorators import login_required

import json


def make_response_view(request, questionnaire):

    form = ResponseForm(questionnaire)
    return render(
        request,
        context={
            'form': form,
            'questionnaire': form.questionnaire
        },
        template_name='responses/response.html'
    )


@login_required
def result(request, questionnaire):

    answ_form = AnswerForm(request.POST)
    if answ_form.is_valid():
        answ = answ_form.save()
    else:
        return render(
            request,
            context = {'error': True},
            template_name='responses/results.html'
    )
    resp = request.POST['response']

    result = result_processor(questionnaire, resp)

    resp = Response.objects.get(pk=resp)
    resp.is_finished = True
    resp.result = json.dumps(result)
    resp.save()

    questionnaire = Questionnaire.objects.get(pk=questionnaire)

    if questionnaire.pk == 1:
        context = {
            'questionnaire': questionnaire,
            'org_level': result['org_level'],
            'com_level': result['com_level'],
            'org_score': result['org_score'],
            'com_score': result['com_score']
        }

    if questionnaire.pk == 2:
        result['questionnaire'] = questionnaire
        context = result
        variants = QuestionnaireResult.objects.filter(questionnaire=questionnaire)
        variant = variants.get(category__name=result['category'])
        items = Item.objects.filter(variant=variant)
        already_items = [i.item.pk for i in ItemUser.objects.filter(user=request.user)]
        items = items.exclude(id__in=already_items)

        if len(items) > 0:
            item = random.choice(items)
            ItemUser(item=item, user=request.user).save()
            context['item_icon'] = item.icon
            context['item_name'] = item.name
            context['no_item'] = False
        else:
            context['no_item'] = True

    return render(
        request,
        context = context,
        template_name='responses/results.html'
    )


@login_required
def start_response_view(request, questionnaire):
    q = Questionnaire.objects.get(pk=questionnaire)
    last_finished = 0
    try:
        unfinished = Response.objects.get(
            questionnaire=questionnaire,
            is_finished=False
        )
        last_finished = unfinished.last_step()
        last_finished += 1
        return question_view(request, questionnaire, last_finished, unfinished)

    except Response.DoesNotExist:
        pass

    except Response.MultipleObjectsReturned:
        responses = Response.objects.filter(
            questionnaire=questionnaire,
            is_finished=False
        )
        for r in responses:
            r.is_finished=True
            r.save()

    form = ResponseForm(initial={
        'questionnaire': q,
        'user': request.user
    })
    context = {
        'questionnaire': q,
        'form': form
    }

    return render(
        request,
        context=context,
        template_name='responses/response.html'
    )


@login_required
def question_view(request, questionnaire, question, resp_obj=None):
    print(question)
    if request.method == 'POST':
        if question == 1:
            resp_form = ResponseForm(request.POST)
            if resp_form.is_valid():
                resp = resp_form.save()
            else:
                resp = resp_form.save()
        else:
            answ_form = AnswerForm(request.POST)
            if answ_form.is_valid():
                answ = answ_form.save()
            else:
                answ = answ_form.save()
            resp = request.POST['response']
    else:
        resp = resp_obj

    Q = Questionnaire.objects.get(pk=questionnaire)
    if question > 1:
        index = question - 1
    else:
        index = 0
    q = Q.questions()[index]
    last = len(Q.questions())
    if question != last:
        next = question + 1
    else:
        next = 'result'

    form = AnswerForm(initial={
        'question': q,
        'response': resp,
    })
    form.fields['body'].queryset = AnswerChoice.objects.filter(
        answer_type=Q.answers_type
    )
    form.fields['body'].widget.attrs.update({'autofocus': 'autofocus'})
    form.fields['body'].widget.attrs.update({'onchange' : "this.form.submit();"})

    progress = (int(question)-1)*100//int(last)

    step_img = (question % 2) + 1
    if ((question + 3) % 10 == 0) and ((question + 3) <= last):
        step_img = 3
    if ((question + 2) % 10 == 0) and ((question + 2) <= last):
        step_img = 4
    if ((question + 1) % 10 == 0) and ((question + 1) <= last):
        step_img = 5
    if (question % 10 == 0) and (question <= last):
        step_img = 6

    if (question+1 % 6 == 0) and (question+1 <= last):
        step_img = 7
    if (question % 6 == 0) and (question <= last):
        step_img = 8

    if question == last:
        step_img = 9

    return render(
        request,
        context={
            'questionnaire': Q,
            'question': q.text,
            'last': last,
            'current': question,
            'next': next,
            'form': form,
            'progress': progress,
            'sprite': int(progress - progress/(progress**2+1)),
            'step_img': step_img
        },
    template_name='responses/question.html'
    )
