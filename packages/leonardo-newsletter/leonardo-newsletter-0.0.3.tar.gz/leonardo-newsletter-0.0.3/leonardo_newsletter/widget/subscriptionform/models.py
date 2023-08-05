from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django.conf import settings
from django.db import models
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from emencia.django.newsletter.forms import (AllMailingListSubscriptionForm,
                                             MailingListSubscriptionForm)
from emencia.django.newsletter.models import MailingList
from leonardo import messages
from leonardo.module.web.models import Widget


class EmailSubscriptionForm(MailingListSubscriptionForm):

    class Meta(MailingListSubscriptionForm.Meta):
        fields = ['email']


class EmailAllSubscriptionForm(AllMailingListSubscriptionForm):

    class Meta(AllMailingListSubscriptionForm.Meta):
        fields = ['email']


class SubscriptionFormWidget(Widget):

    """CMS Plugin for susbcribing to a mailing list"""
    title = models.CharField(_('title'), max_length=100, blank=True)
    show_description = models.BooleanField(_('show description'), default=True,
                                           help_text=_('Show the mailing list\'s description.'))
    mailing_list = models.ForeignKey(MailingList, verbose_name=_('mailing list'),
                                     help_text=_(
                                         'Mailing List to subscribe to.'),
                                     blank=True, null=True)
    just_email = models.BooleanField(_('Show just email'), default=False,
                                     help_text=_('Show just email input.'))
    subscribe_all = models.BooleanField(_('Subscribe all mailing lists'), default=False,
                                        help_text=_('Subscribe all mailing lists.'))

    form_layout = models.TextField(
        _('Form Layout'), blank=True, null=True,
        help_text=_('Crispy Form Layout see \
            http://django-crispy-forms.readthedocs.org/en/latest/layouts.html \
            \n Advanced users only ! \n'))

    def __unicode__(self):
        return self.mailing_list.name

    def render(self, **kwargs):
        request = kwargs['request']
        context = RequestContext(
            request,
            {
                'widget': self,
            }
        )
        form_name = self.fe_identifier

        if self.just_email:
            if self.subscribe_all:
                form_cls = EmailAllSubscriptionForm
            else:
                form_cls = EmailSubscriptionForm
        else:
            if self.subscribe_all:
                form_cls = AllMailingListSubscriptionForm
            else:
                form_cls = MailingListSubscriptionForm

        if request.method == "POST" and (form_name in request.POST.keys()):
            form = form_cls(data=request.POST)
            if form.is_valid():
                form.save(self.mailing_list)
                form.saved = True
        else:
            form = form_cls()

        form.helper = FormHelper(form)
        form.helper.form_tag = False

        if self.form_layout:

            try:
                form.helper.layout = eval(self.form_layout)
            except Exception as e:
                if settings.DEBUG:
                    messages.error(request, str(e))
        else:
            # use default layout
            form.helper.layout = Layout(
                ButtonHolder(
                    FieldWithButtons(Field('email', placeholder=_('Email')),
                                     Submit('submit', _('Subscribe'),
                                            css_class='btn-default'))
                )
            )

            # we must append mailing list fields
            layout = form.helper.layout
            for field in form.hidden_fields():
                layout.append(Field(field.name, placeholder=field.label))

            form.helper.form_show_labels = False

        context.update({
            'object': self.mailing_list,
            'form': form,
            'request': request,
            'form_name': form_name,
        })
        return self.render_response(context)

    class Meta:
        abstract = True
        verbose_name = _('Newsletter Subscription Form')
        verbose_name_plural = _('Newsletter Subscription Forms')
