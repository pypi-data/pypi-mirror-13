from __future__ import absolute_import

from celery import shared_task
from django.core import management


@shared_task
def send_newsletter():
    management.call_command('send_newsletter', interactive=False)
    return {'result': 'Sending newsletters OK'}
