from __future__ import absolute_import, unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from .models import Test


@shared_task
def delete_test(id):
    try:
        Test.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return 'object does not exist!'
    return 'delete is done!'