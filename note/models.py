from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Question(models.Model):
    text = models.CharField(_('text'), max_length=300)

    def __str__(self):
        return f'{self.text}'


class Test(models.Model):
    name = models.CharField(_('name'), max_length=100)
    questions = models.ManyToManyField(Question)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = GenericRelation('NotedItem')

    def __str__(self):
        return f'{self.name}'


class RunTest(models.Model):
    name = models.CharField(_('name'), max_length=100)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = GenericRelation('NotedItem')

    def __str__(self):
        return f'{self.name}'


class RunTestAnswers(models.Model):
    run_test = models.ForeignKey(RunTest, on_delete=models.CASCADE, related_name='run_test')
    question = models.CharField(_('question'), max_length=300)
    answer = models.CharField(_('answer'), max_length=300)

    def __str__(self):
        return f'run_test "{self.run_test}", question: {self.question}, answer: {self.answer}'


class NotedItem(models.Model):
    note = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.content_type, self.object_id, self.note}'


