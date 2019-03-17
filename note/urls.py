from django.urls import path, include
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('question/delete/<int:q_id>', views.delete_question, name='delete_question'),
    path('new_<str:new_object>', views.new_object, name='new_object'),

    path('tests/<int:test_id>/remove/<int:q_id>', views.remove_q, name='remove_q'),
    path('tests/<int:test_id>/add/<int:q_id>', views.add_q, name='add_q'),

    path('tests/<int:test_id>', views.detail_of_test, name='detail_of_test'),
    path('tests/<int:test_id>/edit', views.edit_test, name='edit_test'),
    path('tests/<int:test_id>/delete', views.test_delete, name='delete_test'),
    path('tests/<int:test_id>/run', views.run_test, name='run_test'),
    path('tests/run_tests/<int:runtest_id>', views.run_test_detail, name='run_test_detail'),

    path('<str:model_object>/<int:obj_id>/notes/', views.model_notes, name='model_notes'),

    path('user/logout', views.logout_view, name='logout'),
    path('user/signup', views.sign_up, name='signup'),
    path('user/login', views.login_view, name='login'),

    path('i18n/', include('django.conf.urls.i18n'), name='set_language'),
]