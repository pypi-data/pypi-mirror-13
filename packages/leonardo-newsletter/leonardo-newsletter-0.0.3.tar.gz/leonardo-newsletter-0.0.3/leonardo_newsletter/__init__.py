
from django.apps import AppConfig

default_app_config = 'leonardo_newsletter.Config'


LEONARDO_APPS = [
    'leonardo_newsletter',
    'emencia.django.newsletter',
    'tagging'
]

LEONARDO_OPTGROUP = 'Newsletter'

LEONARDO_WIDGETS = [
    'leonardo_newsletter.widget.subscriptionform.models.SubscriptionFormWidget'
]

LEONARDO_PLUGINS = [
    ('leonardo_newsletter.apps.newsletter', 'Newsletter Mailing Lists'),
]


class Config(AppConfig):
    name = 'leonardo_newsletter'
    verbose_name = "leonardo-newsletter"
