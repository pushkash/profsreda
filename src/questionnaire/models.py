from django.db import models


class Questionnaire(models.Model):
    name = models.CharField(
        max_length=400,
        unique=True,
        verbose_name="Название"
    )
    description = models.TextField(
        verbose_name="Описание"
    )
    answers_type = models.ForeignKey(
        'AnswerType',
        on_delete=models.PROTECT,
        verbose_name="Тип ответов",
        help_text=""
    )

    class Meta:
        verbose_name = 'Анкета теста'
        verbose_name_plural = 'Анкеты тестов'

    def __str__(self):
        return self.name

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "questions": self.questions(),
        }

    def questions(self):
        if self.id:
            questions = []
            for question in Question.objects.filter(questionnaire=self.id):
                questions.append({
                    "sort_id": question.sort_id,
                    "text": question.text,
                    "answers": [
                        {
                            "value": 0,
                            "transcript": "Нет",
                            "weight": 1,
                            "category": "Тип 1"
                        },
                        {
                            "value": 1,
                            "transcript": "Да",
                            "weight": 1,
                            "category": "Тип 2"
                        },
                    ],
                })
            return questions
        else:
            return None


class Category(models.Model):
    name = models.CharField(
        max_length=400,
        verbose_name="Название категории",
        unique=True,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Question(models.Model):
    text = models.TextField(
        verbose_name="Текст вопроса"
    )
    sort_id = models.PositiveIntegerField(
        verbose_name="Порядковый номер в опроснике"
    )
    questionnaire = models.ForeignKey(
        'Questionnaire',
        on_delete=models.PROTECT,
        verbose_name='Опрос'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT,
        verbose_name='Категория',
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = (('sort_id', 'questionnaire'),)
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return "{} из {}".format(self.sort_id, self.questionnaire.name)

    def get_choices(self):
        choices = self.questionnaire.answers_type.answerchoice_set
        return choices.all()


class AnswerType(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название",
        unique=True
    )

    class Meta:
        verbose_name = "Тип ответа"
        verbose_name_plural = "Типы ответов"

    def __str__(self):
        return self.name


class AnswerChoice(models.Model):
    choice = models.CharField(
        max_length=100,
        verbose_name="Текст варианта"
    )
    answer_type = models.ForeignKey(
        'AnswerType',
        on_delete=models.PROTECT
    )

    class Meta:
        unique_together = (
            ('answer_type', 'choice'),
        )
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

    def __str__(self):
        return self.choice
