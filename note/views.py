import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404, HttpResponseRedirect
from django.forms.models import formset_factory
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from .models import Question, Test, RunTest, RunTestAnswers, NotedItem
from .forms import TestForm, QuestionForm, AnswerForm, NoteForm
from .tasks import delete_test


def index(request):
    tests = None
    questions = None
    context = {}
    if 'search' in request.GET:
        tests = Test.objects.filter(name__icontains=request.GET['title'])
    elif request.method == 'GET':
        tests = Test.objects.all()
        questions = Question.objects.all()

    #if request.user.is_authenticated:
    #    token, created = Token.objects.get_or_create(user=request.user)
    #    context.update(token=token)

    context.update(tests=tests, questions=questions)
    return render(request, 'test/index.html', context=context)


def new_object(request, new_object):
    MINUTES = '20'
    DAYS = '30'

    context = {'name': new_object}
    if request.method == 'POST':
        if new_object == 'test':
            new_test = TestForm(request.POST)
            if new_test.is_valid():
                named_test = new_test.save(commit=False)
                if request.user.is_authenticated:
                    named_test.user = request.user
                else:
                    named_test.user = None
                named_test.save()

                if new_test.cleaned_data['delay'] == MINUTES:
                    minutes = int(new_test.cleaned_data['count'])
                    time_to_exp = now() + timedelta(minutes=minutes)
                    delete_test.apply_async((named_test.id,), eta=time_to_exp)

                elif new_test.cleaned_data['delay'] == DAYS:
                    days = int(new_test.cleaned_data['count'])
                    time_to_exp = now() + timedelta(days=days)
                    delete_test.apply_async((named_test.id,), eta=time_to_exp)

        elif new_object == 'question':
            new_question = QuestionForm(request.POST)
            if new_question.is_valid():
                new_question.save()
            return redirect('/new_question')

        return redirect('/')

    elif request.method == 'GET':
        if new_object == 'test':
            name = _('test')
            context.update(form=TestForm, name=name)
        elif new_object == 'question':
            name = _('question')
            questions = Question.objects.all()
            context.update(form=QuestionForm, questions=questions, name=name)

        return render(request, 'test/new_object.html', context=context)


def delete_question(request, q_id):
    Question.objects.get(id=q_id).delete()

    return new_object(request, 'question')


def detail_of_test(request, test_id):
    context = {}
    if request.method == 'GET':
        tests = get_object_or_404(Test, id=test_id)
        questions = tests.questions.all()
        run_tests = RunTest.objects.filter(test=tests)
        context.update(test=tests, questions=questions, run_tests=run_tests)
        return render(request, 'test/test_info.html', context=context)


def edit_test(request, test_id):
    context = {}

    if request.method == 'GET':
        test = get_object_or_404(Test, id=test_id)
        test_questions = test.questions.all()
        questions = Question.objects.all()

        context.update(test=test,
                       test_questions=test_questions,
                       questions=questions)
        return render(request, 'test/edit_test.html', context=context)


def test_delete(request, test_id):
    get_object_or_404(Test, id=test_id).delete()
    return redirect('/')


def remove_q(request, test_id, q_id):
    if request.method == 'POST':
        test = get_object_or_404(Test, id=test_id)
        question = get_object_or_404(Question, id=q_id)

        test.questions.remove(question)
        return redirect(f'/tests/{test_id}/edit')


def add_q(request, test_id, q_id):
    if request.method == 'POST':
        test = Test.objects.get(id=test_id)
        question = Question.objects.get(id=q_id)

        test.questions.add(question)
        return redirect(f'/tests/{test_id}/edit')


def run_test(request, test_id):

    context={}

    if not request.user.is_authenticated:
        form = UserCreationForm()
        context.update(form=form)
        return render(request, 'test/signup_v.html', context=context)

    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()
    answer_factory = formset_factory(AnswerForm, min_num=len(questions))
    answer_form_set = answer_factory()

    if request.method == 'POST':
        answer_form_set = answer_factory(request.POST)
        if answer_form_set.is_valid():
            if request.user.is_authenticated:
                user_name = request.user
            else:
                user_name = None
            run_test_obj = RunTest(name=test.name, test=test, user=user_name)
            run_test_obj.save()
            for q, a in zip(questions, answer_form_set.cleaned_data):
                run_test_answer = RunTestAnswers(run_test=run_test_obj, question=str(q), answer=a['Answer'])
                run_test_answer.save()
            return redirect(f'/tests/{test_id}')

    context = {'formset': dict(zip(questions, answer_form_set)),
               'manage_form': answer_form_set,
               'test': test}
    return render(request, 'test/start_quiz.html', context=context)


def run_test_detail(request, runtest_id):
    run_test_obj = get_list_or_404(RunTest, id=runtest_id)
    run_tests_answers = get_list_or_404(RunTestAnswers, run_test__in=run_test_obj)

    context = {'run_test': run_test_obj, 'run_tests_answers': run_tests_answers}

    return render(request, 'test/run_test_detail.html', context=context)


def model_notes(request, model_object, obj_id):
    model_map = {'tests': Test,
                 'run_tests': RunTest}

    run_test_obj = model_map[model_object].objects.get(id=obj_id)
    context = {'type_info': run_test_obj.name,
               'form': NoteForm,
               'notes_obj': NotedItem.objects.filter(content_type=ContentType.objects.get_for_model(run_test_obj),
                                                     object_id=obj_id)}

    if request.method == 'POST':
        note_form = NoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.cleaned_data['note']
            note_item = NotedItem(note=note,
                                  content_type=ContentType.objects.get_for_model(run_test_obj),
                                  object_id=obj_id)
            note_item.save()
        else:
            context.update(form=note_form)

    return render(request, 'test/notes.html', context=context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def sign_up(request):
    context = {}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
        else:
            context = {'form': form}
            return render(request, 'test/login_v.html', context=context)
    elif request.method == 'GET':
        form = UserCreationForm()
        context.update(form=form)
        return render(request, 'test/signup_v.html', context=context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
        else:
            context = {'form': form}
            return render(request, 'test/login_v.html', context=context)
    else:
        form = AuthenticationForm()
        context = {'form': form}
        return render(request, 'test/login_v.html', context=context)

