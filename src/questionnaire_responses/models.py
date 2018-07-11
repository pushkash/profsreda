from django.db import models
from django.contrib.auth.models import User
from questionnaire.models import Questionnaire, Question, AnswerChoice, Category


class Response(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Пользователь",
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата прохождения",
    )
    questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.PROTECT,
        verbose_name="Тест"
    )
    is_finished = models.BooleanField(
        default=False
    )
    result = models.TextField(
        default='{}'
    )

    class Meta:
        verbose_name = "Прохождение теста"
        verbose_name_plural = "Прохождения тестов"

    def __str__(self):
        return "Ответы на тест {} от пользователя {} за {}".format(
            self.questionnaire.name,
            self.user.pk,
            self.created
        )

    def last_step(self):
        last_answer = self.answer_set.last()
        if last_answer is not None:
            return last_answer.question.sort_id
        else:
            return 0


class Answer(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT
    )
    response = models.ForeignKey(
        Response,
        on_delete=models.PROTECT
    )
    body = models.ForeignKey(
        AnswerChoice,
        on_delete=models.PROTECT,
        verbose_name='Ответ'
    )

    class Meta:
        verbose_name = "Ответ на вопрос из анкеты"
        verbose_name_plural = "Ответы на вопросы из анкет"


class QuestionnaireResult(models.Model):
    questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.PROTECT
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT
    )
    main_description = models.TextField()
    description1 = models.TextField(default="", blank=True)
    description2 = models.TextField(default="", blank=True)
    description3 = models.TextField(default="", blank=True)

    class Meta:
        verbose_name = 'Описание результата'
        verbose_name_plural = 'Описания результатов'
        unique_together = (('questionnaire', 'category'),)

    def __str__(self):
        return "{}: {}".format(self.questionnaire.name, self.category.name)


class ResponseResult(models.Model):
    qr = models.ForeignKey(
        QuestionnaireResult,
        on_delete=models.PROTECT
    )
    response = models.ForeignKey(
        Response,
        on_delete=models.PROTECT
    )
    score = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Результат прохождения'
        verbose_name_plural = 'Результаты прохождений'
