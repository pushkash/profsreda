from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Test(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Название"),
        help_text=_("Название теста")
    )
    description = models.TextField(
        max_length=1000,
        verbose_name=_("Описание"),
        help_text=_("Описание теста")
    )
    image = models.ImageField(
        upload_to="test_images/",
        verbose_name=_("Обложка"),
        help_text=_("Обложка теста")
    )

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def __str__(self):
        return self.name

    def get_questions(self):
        """
        Returns related questions
        :return: QuerySet of related questions
        """
        return Question.objects.filter(test=self.id)

    def get_categories(self):
        """
        Returns related categories
        :return: QuerySet of related categories
        """
        return Category.objects.filter(test=self.id)

    def main_dict(self):
        """
        Returns main info about test
        :return: dict with main info about test
        """
        test = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image.url,
        }
        return test

    def dict(self):
        """
        Returns full info about test
        :return: dict with full info about test
        """
        questions = [question.dict() for question in self.get_questions()]
        categories = [category.dict() for category in self.get_categories()]
        test = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image.url,
            "questions": questions,
            "categories": categories
        }
        return test


class Question(models.Model):
    test = models.ForeignKey(
        "tests.Test",
        on_delete=models.CASCADE,
        verbose_name=_("Тест"),
        help_text=_("Тест, к которому относится вопрос")
    )
    text = models.CharField(
        max_length=100,
        verbose_name=_("Вопрос"),
        help_text=_("Текст вопроса")
    )

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return " - ".join([str(self.test), self.text])

    def get_answer_categories(self):
        """
        Returns related answer-category objects
        :return: QuerySet of related answer-category objects
        """
        return AnswerCategory.objects.filter(question=self.id)

    def get_answer_category(self, answer_text):
        """
        Returns answer-category object with given answer text
        :param answer_text: key to find answer-category object
        :return: AnswerCategory with given answer text
        """
        return AnswerCategory.objects.filter(question=self.id,
                                             answer_text=answer_text)

    def dict(self):
        """
        Returns all info about question
        :return: dict with all info about question
        """
        answer_categories = [answer_category.dict() for answer_category in self.get_answer_categories()]
        question = {
            "id": self.id,
            "text": self.text,
            "answer_categories": answer_categories
        }
        return question


class AnswerCategory(models.Model):
    answer_text = models.CharField(
        max_length=100,
        verbose_name=_("Ответ"),
        help_text=_("Текст ответа")
    )
    question = models.ForeignKey(
        "tests.Question",
        on_delete=models.CASCADE,
        verbose_name=_("Вопрос"),
        help_text=_("Соответствующий ответу вопрос")
    )
    category = models.ForeignKey(
        "tests.Category",
        on_delete=models.CASCADE,
        verbose_name=_("Категория"),
        help_text=_("Категория, соответствующая ответу")
    )
    weight = models.PositiveIntegerField(
        verbose_name=_("Коэффициент"),
        help_text=_("Коэффициент, с которым ответ учитывается при подсчёте результата")
    )

    class Meta:
        verbose_name = "Ответ-Категория"
        verbose_name_plural = "Пары Ответ-Категория"

    def __str__(self):
        return " - ".join([str(self.question), self.answer_text, str(self.category)])

    def dict(self):
        """
        Returns all info about answer-category
        :return: dict with all info about answer-category
        """
        answer_category = {
            "id": self.id,
            "answer_text": self.answer_text,
            "category_id": self.category.id,
            "weight": self.weight
        }
        return answer_category


class Category(models.Model):
    test = models.ForeignKey(
        "tests.Test",
        on_delete=models.CASCADE,
        verbose_name=_("Тест"),
        help_text=_("Тест, определяющий данную категорию")
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Название"),
        help_text=_("Название категории")
    )
    short_description = models.TextField(
        max_length=1000,
        verbose_name=_("Описание"),
        help_text=_("Краткое описание категории")
    )
    long_description = models.TextField(
        max_length=10000,
        blank=True,
        null=True,
        verbose_name=_("Развернутое описание"),
        help_text=_("Развёрнутое описание категории")
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return " - ".join([str(self.test), self.name])

    def dict(self):
        """
        Returns all info about category
        :return: dict with all info about category
        """
        category = {
            "id": self.id,
            "name": self.name,
            "short_description": self.short_description,
            "long_description": self.long_description
        }
        return category


# TODO: add result categories
class TestResult(models.Model):
    test_session = models.ForeignKey(
        "tests.TestSession",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Тест сессия"),
        help_text=_("Тест сессия, которой соответствует результат")
    )
    item = models.ForeignKey(
        "heroes.Item",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Награда"),
        help_text=_("Предмет, полученный в награду за прохождение теста")
    )

    class Meta:
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестов"


class TestSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Тестируемый"),
        help_text=_("Пользователь, проходящий тест")
    )
    test = models.ForeignKey(
        "tests.Test",
        on_delete=models.CASCADE,
        verbose_name=_("Тест"),
        help_text=_("Тест, к которому относиться сессия")
    )
    last_answered_question = models.ForeignKey(
        "tests.Question",
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Последний отвеченный вопрос"),
        help_text=_("Последний вопрос, на который ответил пользователь")
    )
    is_finished = models.BooleanField(
        default=False,
        verbose_name=_("Закончена"),
        help_text=_("Значение, указывающее, закончена ли тест сессия")
    )

    class Meta:
        verbose_name = "Тест сессия"
        verbose_name_plural = "Тест сессии"

    def __str__(self):
        return " - ".join([str(self.user), str(self.test), "Закончен" if self.is_finished else "Не закончен"])

    def get_answers(self):
        """
        Returns all session answers
        :return: QuerySet of session answers
        """
        return Answer.objects.filter(test_session=self.id)

    def check_is_finished(self):
        """
        Checks if test is finished
        :return:
        """
        # Check if answers count = questions count
        self.is_finished = Answer.objects.filter(test_session=self).count() == self.test.get_questions().count()
        self.save()
        return self.is_finished

    def dict(self):
        """
        Returns main info about test session
        :return: dict with main info about test session
        """
        test_session = {
            "id": self.id,
            "last_answered_question": None if self.last_answered_question is None else self.last_answered_question.dict()
        }
        return test_session


class Answer(models.Model):
    test_session = models.ForeignKey(
        "tests.TestSession",
        on_delete=models.CASCADE,
        verbose_name=_("Тест сессия"),
        help_text=_("Тест сессия, в которую был сделан ответ")
    )
    question = models.ForeignKey(
        "tests.Question",
        on_delete=models.CASCADE,
        verbose_name=_("Вопрос"),
        help_text=_("Вопрос, к которому относится ответ")
    )
    answer_text = models.CharField(
        max_length=100,
        verbose_name=_("Ответ"),
        help_text=_("Текст ответа")
    )

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return " - ".join([str(self.test_session), str(self.question), self.answer_text])
