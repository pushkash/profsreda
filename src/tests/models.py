from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from heroes.models import Item, ItemUser


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

    def get_user_result(self, user):
        """
        Returns last test result for given user
        :param user: user to find test result
        :return: last TestResult object for given user
        """
        return TestResult.objects.filter(test_session__test=self,
                                         test_session__user=user).last()

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
            "categories": categories,
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
        max_length=150,
        verbose_name=_("Вопрос"),
        help_text=_("Текст вопроса")
    )

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return " - ".join([str(self.test), self.text])

    def get_answers(self):
        """
        Returns related answer-category objects
        :return: QuerySet of related answer-category objects
        """
        return Answer.objects.filter(question=self.id)

    def get_answer(self, answer_text):
        """
        Returns answer-category object with given answer text
        :param answer_text: key to find answer-category object
        :return: AnswerCategory with given answer text
        """
        return Answer.objects.filter(question=self.id,
                                     answer_text=answer_text)

    def dict(self):
        """
        Returns all info about question
        :return: dict with all info about question
        """
        answer_categories = [answer_category.dict() for answer_category in self.get_answers()]
        question = {
            "id": self.id,
            "text": self.text,
            "answers": answer_categories
        }
        return question


class Answer(models.Model):
    answer_text = models.CharField(
        max_length=100,
        verbose_name=_("Ответ"),
        help_text=_("Текст ответа")
    )
    question = models.ForeignKey(
        "tests.Question",
        on_delete=models.CASCADE,
        verbose_name=_("Вопрос"),
        help_text=_("Соответствующий варианту ответа вопрос")
    )
    category = models.ForeignKey(
        "tests.Category",
        on_delete=models.CASCADE,
        verbose_name=_("Категория"),
        help_text=_("Категория, соответствующая варианту ответа")
    )
    weight = models.PositiveIntegerField(
        verbose_name=_("Коэффициент"),
        help_text=_("Коэффициент, с которым вариант ответа учитывается при подсчёте результата")
    )

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

    def __str__(self):
        return " - ".join([str(self.question), self.answer_text, str(self.category)])

    def dict(self):
        """
        Returns all info about answer-category
        :return: dict with all info about answer-category
        """
        answer = {
            "id": self.id,
            "text": self.answer_text,
            "category_id": self.category.id,
            "weight": self.weight
        }
        return answer


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


class TestResult(models.Model):
    test_session = models.ForeignKey(
        "tests.TestSession",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Тест сессия"),
        help_text=_("Тест сессия, которой соответствует результат")
    )

    class Meta:
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестов"

    def get_test(self):
        """
        Returns Test related to TestResult
        Only for code readability
        :return: Test object
        """
        return self.test_session.test

    def get_result_categories(self):
        """
        Returns all related ResultCategory objects
        :return: QuerySet of related ResultCategory
        """
        return ResultCategory.objects.filter(test_result=self)

    def get_result_items(self):
        """
        Returns all related ResultItem objects
        :return: QuerySet of related ResultItem
        """
        return ResultItem.objects.filter(test_result=self)

    def dict(self):
        """
        Returns info about TestResult
        :return: dict with info about TestResult
        """
        result_categories = [rc.dict() for rc in self.get_result_categories()]
        result_items = [ri.dict() for ri in self.get_result_items()]
        test_result = {
            "id": self.id,
            "categories": result_categories,
            "items": result_items
        }
        return test_result


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
    next_question_to_answer = models.ForeignKey(
        "tests.Question",
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Следующий вопрос"),
        help_text=_("Следующий вопрос, на который нужно ответить"),
        related_name="next_answer"
    )
    count_answered_questions = models.PositiveSmallIntegerField(
        default=0, verbose_name=_("Количество отвеченных вопросов"),
        help_text=_("Количество вопросов, на которые ответил пользователь")
    )
    is_finished = models.BooleanField(
        default=False,
        verbose_name=_("Закончена"),
        help_text=_("Значение, указывающее, закончена ли тест сессия")
    )
    datetime_created = models.DateTimeField(
        verbose_name=_("Время старта"),
        help_text=_("Время, в которое пользователь начал проходить тест")
    )
    datetime_finished = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Время завершения"),
        help_text=_("Время, в которое пользователь закончил проходить тест")
    )

    class Meta:
        verbose_name = "Тест сессия"
        verbose_name_plural = "Тест сессии"

    def __str__(self):
        return " - ".join([str(self.user), str(self.test), "Закончен" if self.is_finished else "Не закончен"])

    def get_responses(self):
        """
        Returns all session responses
        :return: QuerySet of session responses
        """
        return Response.objects.filter(test_session=self.id)

    def check_is_finished(self):
        """
        Checks if test is finished
        :return:
        """
        # Check if answers count = questions count
        self.is_finished = self.count_answered_questions == self.test.get_questions().count()
        self.save()

        return self.is_finished

    def finish(self):
        """
        Creates TestResult, ResultCategory, ResultItem
        :return:
        """
        self.datetime_finished = timezone.now()
        self.save()
        test_result = TestResult.objects.create(test_session=self)

        for result_category in self.calculate_result_categories():
            ResultCategory.objects.create(test_result=test_result,
                                          category=result_category)
            for item in Item.objects.filter(category=result_category):
                try:
                    user_item = ItemUser.objects.get(item=item,
                                                     user=self.user)
                except ItemUser.DoesNotExist:
                    ResultItem.objects.create(test_result=test_result,
                                              item=item)
                    user_item = ItemUser.objects.create(item=item,
                                                        user=self.user)

    def calculate_result_categories(self):
        """
        Calculates categories weights
        :return: list of categories with max weight
        """
        categories_weights = {category: 0 for category in Category.objects.filter(test=self.test)}
        for response in Response.objects.filter(test_session=self):
            categories_weights[response.answer.category] += response.answer.weight
        max_weight = max(categories_weights.values())

        result_categories = [category for category, weight in categories_weights.items() if weight == max_weight]
        return result_categories

    def dict(self):
        """
        Returns main info about test session
        :return: dict with main info about test session
        """
        test_session = {
            "id": self.id,
            "last_answered_question": None if self.last_answered_question is None else self.last_answered_question.dict(),
            "next_question_to_answer": None if self.next_question_to_answer is None else self.next_question_to_answer.dict(),
            "count_answered_questions": self.count_answered_questions,
            "is_finished": self.is_finished
        }
        return test_session


class Response(models.Model):
    test_session = models.ForeignKey(
        "tests.TestSession",
        on_delete=models.CASCADE,
        verbose_name=_("Тест сессия"),
        help_text=_("Тест сессия, в которую был сделан ответ")
    )
    answer = models.ForeignKey(
        "tests.Answer",
        on_delete=models.CASCADE,
        verbose_name=_("Вариант ответа"),
        help_text=_("Выбранный вариант ответа")
    )
    datetime_created = models.DateTimeField(
        verbose_name=_("Время ответа"),
        help_text=_("Время, в которое был сделан ответ")
    )

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return " - ".join([str(self.test_session), str(self.answer)])


class ResultCategory(models.Model):
    test_result = models.ForeignKey(
        "tests.TestResult",
        on_delete=models.CASCADE,
        verbose_name=_("Результат теста"),
        help_text=_("Результат теста, в котором определена категория")
    )
    category = models.ForeignKey(
        "tests.Category",
        on_delete=models.CASCADE,
        verbose_name=_("Категория"),
        help_text=_("Категория, определённая в тесте")
    )

    class Meta:
        verbose_name = "Определённая категория"
        verbose_name_plural = "Определённые категории"

    def __str__(self):
        return " - ".join([str(self.test_result), str(self.category)])

    def dict(self):
        """
        Returns info about ResultCategory
        :return: dict with info about ResultCategory
        """
        result_category = {
            "id": self.id,
            "category": self.category.dict()
        }
        return result_category


class ResultItem(models.Model):
    test_result = models.ForeignKey(
        "tests.TestResult",
        on_delete=models.CASCADE,
        verbose_name=_("Результат теста"),
        help_text=_("Результат теста, за который получена награда")
    )
    item = models.ForeignKey(
        "heroes.Item",
        on_delete=models.CASCADE,
        verbose_name=_("Награда"),
        help_text=_("Награда, полученная за прохождение теста")
    )

    class Meta:
        verbose_name = "Полученная награда"
        verbose_name_plural = "Полученные награды"

    def __str__(self):
        return " - ".join([str(self.test_result), str(self.item)])

    def dict(self):
        """
        Returns info about ResultItem
        :return: dict with info about ResultItem
        """
        result_item = {
            "id": self.id,
            "item": self.item.main_dict()
        }
        return result_item
