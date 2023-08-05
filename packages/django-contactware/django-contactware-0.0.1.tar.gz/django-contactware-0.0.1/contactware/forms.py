import warnings
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.utils.html import simple_email_re

from toolware.utils.mixin import CleanSpacesMixin

from .models import ContactMessage
from .utils import check_email
from .utils import check_spam
from . import defaults as defs


class ContactForm(CleanSpacesMixin, forms.ModelForm):

    required_css_class = 'required_field'

    def __init__(self, *args, **kwargs):
        """
        Check for the required configuration settings
        """

        self.request = kwargs.pop('request')
        super(ContactForm, self).__init__(*args, **kwargs)

        self.fields['referrer'].widget = forms.HiddenInput()

        if not defs.CONTACTWARE_DEFAULT_FROM_EMAIL:
            raise ValidationError(_("You need to set DEFAULT_FROM_EMAIL in your settings"))
        if not defs.CONTACTWARE_DEFAULT_TO_EMAILS:
            raise ValidationError(_("You need to set MANAGERS in your settings"))

        self.site = Site.objects.get_current()
        self.email_sent = False

    def get_message_subject(self):
        """ Returns the rendered version of the message subject without linebreak """

        subject = loader.render_to_string(
            defs.CONTACTWARE_MESSAGE_SUBJECT_TEMPLATE, self.get_rendering_context())
        return ''.join(subject.splitlines())

    def get_message_body(self):
        """ Returns the rendered version of the message body """

        return loader.render_to_string(
            defs.CONTACTWARE_MESSAGE_BODY_TEMPLATE, self.get_rendering_context())

    def get_message_dict(self):
        """ Returns a dict with all required fields for the email to be sent out """

        message_dict = {
            "subject": self.get_message_subject(),
            "message": self.get_message_body(),
            "from_email": defs.CONTACTWARE_DEFAULT_FROM_EMAIL,
            "recipient_list": defs.CONTACTWARE_DEFAULT_TO_EMAILS,
        }
        return message_dict

    def get_rendering_context(self):
        """ Returns the context using which the subject/message is rendered """
        extra_context = dict(self.cleaned_data, site=self.site, time=timezone.now())
        return RequestContext(self.request, extra_context)

    def clean_email(self):
        """ If email is real and vouched for by the provider """
        email = self.cleaned_data['email']
        if not simple_email_re.match(email):
            raise forms.ValidationError(_('Invalid email address'))
        return email

    def save(self, fail_silently=False, commit=True, *args, **kwargs):
        """ Send the email out if send flag is set, Save to DB if flag is Set """

        if defs.CONTACTWARE_SEND_EMAIL and not self.email_sent:
            send_mail(fail_silently=fail_silently, **self.get_message_dict())
            self.email_sent = True
            commit = defs.CONTACTWARE_STORE_DB
        return super(ContactForm, self).save(commit, *args, **kwargs)

    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message', 'referrer',)
