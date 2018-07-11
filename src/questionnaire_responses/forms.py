from .models import Answer, Response
from django import forms


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ('user', 'questionnaire')
        widgets = {
            'user': forms.HiddenInput(),
            'questionnaire': forms.HiddenInput(),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('question', 'response', 'body')
        widgets = {
            'question': forms.HiddenInput(),
            'response': forms.HiddenInput(),
        }
