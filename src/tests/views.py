import json

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status

from tests.models import Test, TestSession, Question, Answer, Response, TestResult, ResultCategory, ResultItem


def get_all_tests(request):
    """
    Returns main information about all tests
    :param request: http request
    :return: JSON object with all tests
    """
    user = request.user
    tests = [test.main_dict() for test in Test.objects.all() if test.check_grade(user)]
    return HttpResponse(
        status=status.HTTP_200_OK,
        content=json.dumps({"tests": tests}),
        content_type="application/json"
    )


def get_test(request, test_id):
    """
    Returns test with given id
    :param request: http request
    :param test_id: test id as key
    :return: JSON object with test data
    """
    try:
        test = Test.objects.get(id=test_id)
        return HttpResponse(
            status=status.HTTP_200_OK,
            content=json.dumps({"test": test.dict()}),
            content_type="application/json"
        )
    except Test.DoesNotExist:
        return HttpResponse(
            status=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error_message": "Теста с таким id не существует"}),
            content_type="application/json"
        )


def get_test_session(request, test_id):
    """
    Returns current test session for test
    :param request: http request
    :param test_id: test for which a test session is requested
    :return: JSON object with current/new test session object
    """
    user = request.user
    # Find test or return error
    try:
        test = Test.objects.get(id=test_id)
        # Find unfinished test session or return error
        try:
            test_session = TestSession.objects.filter(user=user,
                                                      test=test).last()
            if test_session is None:
                raise TestSession.DoesNotExist

            return HttpResponse(
                status=status.HTTP_200_OK,
                content=json.dumps({"test_session": test_session.dict()}),
                content_type="application/json"
            )
        except TestSession.DoesNotExist:
            return HttpResponse(
                status=status.HTTP_403_FORBIDDEN,
                content=json.dumps({"error_message": "Тест сессии с таким id не существует"}),
                content_type="application/json"
            )
    except Test.DoesNotExist:
        return HttpResponse(
            status=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error_message": "Теста с таким id не существует"}),
            content_type="application/json"
        )


def create_test_session(request, test_id):
    """
    Returns new test session for test
    :param request: http request
    :param test_id: test id to create related test session
    :return: JSON object with created test session info
    """
    user = request.user
    # Find test or return error
    try:
        test = Test.objects.get(id=test_id)
        # Find existed test session and return error or create new
        try:
            test_session = TestSession.objects.get(user=user,
                                                   test=test,
                                                   is_finished=False)
            return HttpResponse(
                status=status.HTTP_400_BAD_REQUEST,
                content=json.dumps({"error_message": "Тест сессия для этого теста уже существует"}),
                content_type="application/json"
            )
        except TestSession.DoesNotExist:
            first_question = Question.objects.filter(test=test).first()
            test_session = TestSession.objects.create(user=user,
                                                      test=test,
                                                      next_question_to_answer=first_question,
                                                      datetime_created=timezone.now(), )
            return HttpResponse(
                status=status.HTTP_200_OK,
                content=json.dumps({"test_session": test_session.dict()}),
                content_type="application/json"
            )
    except Test.DoesNotExist:
        return HttpResponse(
            status=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error_message": "Теста с таким id не существует"}),
            content_type="application/json"
        )


@csrf_exempt
def save_response(request, test_session_id, question_id):
    """
    Saves response for given question
    :param request: http response
    :param test_session_id: current test session id
    :param question_id: current question_id
    :return: JSON object with error message in case if one of id's is incorrect
    """
    user = request.user
    # Find test session or return error
    try:
        test_session = TestSession.objects.get(id=test_session_id)
        # Find question or return error
        try:
            question = Question.objects.get(id=question_id)
            # Find answer with given id or return error
            try:
                answer_id = json.loads(request.body.decode("utf-8"))["answer_id"]
                answer = Answer.objects.get(id=answer_id)
                # Check if response for question already exists
                try:
                    current_response = Response.objects.get(test_session=test_session,
                                                            answer__question=answer.question)
                    return HttpResponse(
                        status=status.HTTP_403_FORBIDDEN,
                        content=json.dumps({"error_message": "На этот вопрос уже есть ответ"}),
                        content_type="application/json"
                    )
                except Response.DoesNotExist:
                    response = Response.objects.create(test_session=test_session,
                                                       answer=answer,
                                                       datetime_created=timezone.now())
                    # Change last answered question and save changes
                    test_session.count_answered_questions += 1
                    test_session.last_answered_question = question
                    try:
                        test_session.next_question_to_answer = Question.objects.get(id=question.id + 1)
                    except Question.DoesNotExist:
                        test_session.next_question_to_answer = None

                    test_session.save()

                    if test_session.check_is_finished():
                        test_session.finish()
                    return HttpResponse(status=status.HTTP_200_OK)
            except Answer.DoesNotExist:
                return HttpResponse(
                    status=status.HTTP_404_NOT_FOUND,
                    content=json.dumps({"error_message": "Вариант ответа с таким id не существует"}),
                    content_type="application/json"
                )
        except Question.DoesNotExist:
            return HttpResponse(
                status=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"error_message": "Вопроса с таким id не существует"}),
                content_type="application/json"
            )
    except TestSession.DoesNotExist:
        return HttpResponse(
            status=status.HTTP_403_FORBIDDEN,
            content=json.dumps({"error_message": "Тест сессии с таким id не существует"}),
            content_type="application/json"
        )


def get_test_result(request, test_id):
    """
    Returns last TestResult for test with given id
    :param request: http request
    :param test_id: Test id to find TestResult
    :return: JSON object with TestResult info
    """
    user = request.user
    try:
        test = Test.objects.get(id=test_id)
        test_result = TestResult.objects.filter(test_session__user=user,
                                                test_session__test=test).last()

        if test_result is not None:
            return HttpResponse(
                status=status.HTTP_200_OK,
                content=json.dumps({"test_result": test_result.dict()}),
                content_type="application/json"
            )
        else:
            return HttpResponse(
                status=status.HTTP_404_NOT_FOUND,
                content=json.dumps({{"error_message": "Для теста с таким id нет результатов"}}),
                content_type="application/json"
            )
    except Test.DoesNotExist:
        return HttpResponse(
            status=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error_message": "Теста с таким id не существует"}),
            content_type="application/json"
        )


def get_all_tests_view(request):
    """
    Renders test catalog
    :param request:
    :return: rendered HTML
    """
    user = request.user
    tests = [test for test in Test.objects.all() if test.check_grade(user)]
    test_results = [test.get_user_result(user) for test in tests]

    for i in range(len(tests)):    
        setattr(tests[i], 'result', test_results[i])

    return render(request, "responses/tests.html", {"tests": tests,
                                                    "test_results": test_results})


def test_view(request, test_id):
    """
    Renders test overview template
    :param request: http request
    :param test_id: test id to render overview
    :return: rendered HTML template
    """
    user = request.user
    try:
        test = Test.objects.get(id=test_id)
        # Get last TestSession for user
        test_session = TestSession.objects.filter(test=test,
                                                  user=user).last()
        test_result = test.get_user_result(user)
        return render(request, "responses/tester.html", {"test": test,
                                                         "test_session": test_session,
                                                         "test_result": test_result})
    except Test.DoesNotExist:
        return HttpResponse(
            status=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"error_message": "Теста с таким id не существует"}),
            content_type="application/json"
        )


def result_view_by_test(request, test_id):
    """
    Renders test result template
    :param request: http request
    :param test_id: test id to render test result
    :return: rendered HTML template
    """
    user = request.user
    test = Test.objects.get(id=test_id)
    test_result = TestResult.objects.filter(test_session__user=user,
                                            test_session__test=test).last()
    result_categories = test_result.get_result_categories()
    result_items = test_result.get_result_items()

    tests = [test for test in Test.objects.all() if test.check_grade(user)]
    test_results = [test.get_user_result(user) for test in tests]

    return render(request, "responses/results.html", {"test": test,
                                                      "test_result": test_result,
                                                      "result_categories": result_categories,
                                                      "result_items": result_items,
                                                      "tests": tests,
                                                      "test_results": test_results})


def result_view_by_test_result(request, test_result_id):
    """
    Renders test result template
    :param request: http request
    :param test_result_id: test result id to render test result
    :return: rendered HTML template
    """
    user = request.user

    test_result = TestResult.objects.get(id=test_result_id)
    test = test_result.get_test()

    result_categories = test_result.get_result_categories()
    result_items = test_result.get_result_items()

    tests = [test for test in Test.objects.all() if test.check_grade(user)]
    test_results = [test.get_user_result(user) for test in tests]

    return render(request, "responses/results.html", {"test": test,
                                                      "test_result": test_result,
                                                      "result_categories": result_categories,
                                                      "result_items": result_items,
                                                      "tests": tests,
                                                      "test_results": test_results})
