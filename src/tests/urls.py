from django.urls import path
from tests import views

urlpatterns = [
    path(r"get_all_tests/", views.get_all_tests),
    path(r"get_test/<int:test_id>/", views.get_test),
    path(r"test/<int:test_id>/get_test_session/", views.get_test_session),
    path(r"test/<int:test_id>/create_test_session/", views.create_test_session),
    path(r"test/<int:test_id>/result/", views.get_test_result),
    path(r"test_session/<int:test_session_id>/save_question_response/<int:question_id>/", views.save_response),
    path(r"views/all_tests/", views.get_all_tests_view),
    path(r"views/test_view/<int:test_id>/", views.test_view),
    path(r"views/test/<int:test_id>/result/", views.result_view_by_test),
    path(r"views/test_result/<int:test_result_id>/result/", views.result_view_by_test_result)
]
