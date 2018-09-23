from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from heroes.models import Item, ItemUser, Profile


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
    top_categories_count = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_("Количество определяемых категорий"),
        help_text=_("Количество определяемых категорий")
    )
    detect_lying = models.BooleanField(
        default=False,
        verbose_name=_("Определять лживость"),
        help_text=_("Определять лживость пользователя при прохождении")
    )
    lying_critical_value = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Допустимое количество лживых ответов"),
        help_text=_("Допустимое количество лживых ответов, которые может сделать пользователь, "
                    "чтобы результат теста считался валидным")
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
        return Question.objects.filter(test=self)

    def get_categories(self):
        """
        Returns related categories
        :return: QuerySet of related categories
        """
        return Category.objects.filter(test=self)

    def get_user_result(self, user):
        """
        Returns last test result for given user
        :param user: user to find test result
        :return: last TestResult object for given user
        """
        return TestResult.objects.filter(test_session__test=self,
                                         test_session__user=user).last()

    def check_grade(self, user):
        """
        Checks if test is related to users grade
        :param user: user to filter test
        :return: boolean
        """
        profile = Profile.objects.get(user=user)
        grade_intervals = TestGradeInterval.objects.filter(test=self)
        for grade_interval in grade_intervals:
            if grade_interval.min_grade <= int(profile.grade) <= grade_interval.max_grade:
                return True
        return False

    def main_dict(self):
        """
        Returns main info about test
        :return: dict with main info about test
        """
        question_count = self.get_questions().count()
        test = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image.url,
            "question_count": question_count,
        }
        return test

    def dict(self):
        """
        Returns full info about test
        :return: dict with full info about test
        """
        questions = [question.dict() for question in self.get_questions()]
        categories = [category.dict() for category in self.get_categories()]
        question_count = len(questions)
        test = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image.url,
            "questions": questions,
            "question_count": question_count,
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
        return Answer.objects.filter(question=self)

    def get_answer(self, answer_text):
        """
        Returns answer-category object with given answer text
        :param answer_text: key to find answer-category object
        :return: AnswerCategory with given answer text
        """
        return Answer.objects.filter(question=self,
                                     answer_text=answer_text)

    def dict(self):
        """
        Returns all info about question
        :return: dict with all info about question
        """
        answers = [answer.dict() for answer in self.get_answers()]
        question = {
            "id": self.id,
            "text": self.text,
            "answers": answers
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
    is_liar_checking = models.BooleanField(
        default=False,
        verbose_name=_("Определяет лживость"),
        help_text=_("Определяет лживость пользователя")
    )

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

    def __str__(self):
        return " - ".join([str(self.question), self.answer_text])

    def dict(self):
        """
        Returns all info about answer-category
        :return: dict with all info about answer-category
        """
        answer = {
            "id": self.id,
            "text": self.answer_text,
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
    start_weight = models.SmallIntegerField(
        default=0,
        verbose_name=_("Стартовое значение"),
        help_text=_("Стартовое значение")
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


class AnswerCategory(models.Model):
    answer = models.ForeignKey(
        "tests.Answer",
        verbose_name=_("Вариант ответа"),
        help_text=_("Вариант ответа"),
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        "tests.Category",
        verbose_name=_("Категория варианта ответа"),
        help_text=_("Категория, к которой относиться вариант ответа"),
        on_delete=models.CASCADE
    )
    weight = models.SmallIntegerField(
        verbose_name=_("Коэффициент"),
        help_text=_("Коэффициент, с которым вариант ответа учитывается при подсчёте результата")
    )


class TestResult(models.Model):
    test_session = models.ForeignKey(
        "tests.TestSession",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Тест сессия"),
        help_text=_("Тест сессия, которой соответствует результат")
    )
    is_reliable = models.BooleanField(
        default=True,
        verbose_name=_("Достоверный"),
        help_text=_("Является ли результат теста достоверным, либо пользователь лжёт")
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
        return Response.objects.filter(test_session=self)

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

        result_categories = self.calculate_result_categories()
        # Calculate severity ratios only for result categories
        category_ratios = self.calculate_category_ratios(result_categories)
        for category in result_categories:
            # Save severity ratio only for result categorise
            ResultCategory.objects.create(test_result=test_result,
                                          category=category,
                                          severity_ratio=category_ratios[category])
            for item in Item.objects.filter(category=category):
                # Create ResultItem object only for the first user's TestResult
                # for easy return information about given item
                try:
                    user_item = ItemUser.objects.get(item=item,
                                                     user=self.user)
                except ItemUser.DoesNotExist:
                    ResultItem.objects.create(test_result=test_result,
                                              item=item)
                    user_item = ItemUser.objects.create(item=item,
                                                        user=self.user)

        # Pointing if test result is reliable
        if self.test.detect_lying:
            test_result.is_reliable = self.is_reliable()

    def calculate_result_categories(self):
        """
        Calculates categories weights and severity ratios
        :return: list of categories with max weight
        """
        test_categories = Category.objects.filter(test=self.test)

        # Calculate categories weights
        # [IMPORTANT] Category start weight may not be equal to 0
        categories_weights = {category: category.start_weight for category in test_categories}
        for response in Response.objects.filter(test_session=self):
            answer_categories = AnswerCategory.objects.filter(answer=response.answer)
            # Answer may not have AnswerCategory object associated with it
            for answer_category in answer_categories:
                categories_weights[answer_category.category] += answer_category.weight

        # Calculate max category weight
        # Filter categories with max weight
        max_weights = sorted(list(set(categories_weights.values())), reverse=True)[:self.test.top_categories_count]
        result_categories = [category for category in categories_weights if categories_weights[category] in max_weights]

        return result_categories

    def calculate_category_ratios(self, categories):
        """
        Calculates severity ratio for each category of tested categories
        :return: dict of categories with calculated severity ratio
        """

        # Calculate categories severity ratios
        categories_ratio = {}
        for category in categories:
            # Get all AnswerCategory objects which adds weight to category
            answer_categories = AnswerCategory.objects.filter(category=category)
            # Calculate maximum count of answers, which will adds weight to category
            # [IMPORTANT] Answer adds weight to category, not question
            max_answers_count = answer_categories.count()
            # Get list of answers and user responses which add weight to category
            answers = answer_categories.values("answer")
            responses_count = Response.objects.filter(test_session=self, answer__in=answers).count()
            # Calculate severity ratio
            categories_ratio[category] = responses_count / max_answers_count

        return categories_ratio

    def is_reliable(self):
        lying_critical_value = self.test.lying_critical_value
        lying_answers_count = Response.objects.filter(answer__is_liar_checking=True).count()
        # Comparing actual lying answers with their critical count
        return lying_answers_count >= lying_critical_value

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
    severity_ratio = models.FloatField(
        verbose_name=_("Степень выраженности"),
        help_text=_("Степерь выраженности категории у пользователя")
    )
    show_severity_ratio = models.BooleanField(
        default=False,
        verbose_name=_("Считать степень выраженности"),
        help_text=_("Считать степень выраженности категории у пользователя")
    )

    class Meta:
        verbose_name = "Определённая категория"
        verbose_name_plural = "Определённые категории"

    def __str__(self):
        return " - ".join([str(self.test_result), str(self.category)])

    def get_severity_ratio_interpretation(self):
        """
        Interprets severity ratio depends on test severity scale
        :return: str interpretation of severity ratio
        """
        severity_intervals = SeverityScaleInterval.objects.filter(category=self.category)
        for severity_interval in severity_intervals:
            if severity_interval.min_value <= self.severity_ratio <= severity_interval.max_value:
                return severity_interval.interpretation

        return "Уровень выраженности не определён"

    def dict(self):
        """
        Returns info about ResultCategory
        :return: dict with info about ResultCategory
        """
        result_category = {
            "id": self.id,
            "category": self.category.dict(),
        }

        if self.category.test.show_severity_ratio:
            result_category["severity_ratio"] = self.get_severity_ratio_interpretation()

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


class TestGradeInterval(models.Model):
    test = models.ForeignKey(
        "tests.Test",
        on_delete=models.CASCADE,
        verbose_name=_("Тест"),
        help_text=_("Тест, к кото")
    )
    min_grade = models.SmallIntegerField(
        verbose_name=_("Самый младший класс"),
        help_text=_("Самый младший класс в интервале")
    )
    max_grade = models.SmallIntegerField(
        verbose_name=_("Самый старший класс"),
        help_text=_("Самый старший класс в интервале")
    )

    class Meta:
        verbose_name = "Интервал классов"
        verbose_name_plural = "Интервалы классов"

    def __str__(self):
        return " - ".join([str(self.test), str(self.min_grade), str(self.max_grade)])

    def clean(self, *args, **kwargs):
        if self.min_grade < 1 or self.min_grade > 11:
            raise ValidationError(_("Некорректное значение: Самый младший класс"))
        if self.max_grade < 1 or self.max_grade > 11:
            raise ValidationError(_("Некорректное значение: Самый старший класс"))
        if self.min_grade > self.max_grade:
            raise ValidationError(_("Некорректное значение: Самый младший класс больше Самого старшего"))


class SeverityScaleInterval(models.Model):
    category = models.ForeignKey(
        "tests.Category",
        verbose_name=_("Категория"),
        help_text=_("Категория, к которой относится интервал"),
        on_delete=models.CASCADE
    )
    min_value = models.FloatField(
        verbose_name=_("Меньшая граница"),
        help_text=_("Меньшая граница промежутка")
    )
    max_value = models.FloatField(
        verbose_name=_("Большая граница"),
        help_text=_("Большая граница промежутка")
    )
    interpretation = models.CharField(
        max_length=100,
        verbose_name=_("Интерпретация"),
        help_text=_("Строковая интерпретация интервала")
    )

    class Meta:
        verbose_name = "Интервал шкалы выраженности"
        verbose_name_plural = "Интервалы шкалы выраженности"

    def __str__(self):
        return "_".join([str(self.category), str(self.min_value), str(self.max_value)])

    def clean(self, *args, **kwargs):
        if self.min_value < 0 or self.min_value > 1:
            raise ValidationError(_("Некорректное значение: Меньшая граница"))
        if self.max_value < 0 or self.max_value > 1:
            raise ValidationError(_("Некорректное значение: Большая граница"))
        if self.min_value > self.max_value:
            raise ValidationError(_("Некорректное значение: Меньшая граница больше Большей границы"))
