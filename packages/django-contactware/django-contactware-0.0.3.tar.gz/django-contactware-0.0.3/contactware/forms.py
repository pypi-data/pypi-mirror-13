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
    """
    Contact Form.
    """
    required_css_class = 'required_field'
    identifier = 'contact'

    def __init__(self, *args, **kwargs):
        """
        Check for the required configuration settings
        """
        self.request = kwargs.pop('request')
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['identifier'].widget = forms.HiddenInput()
        self.fields['identifier'].initial = self.identifier
        self.fields['referrer'].widget = forms.HiddenInput()
        if self.request.user.is_authenticated():
            self.fields['name'].widget = forms.HiddenInput()
            self.fields['name'].initial = self.request.user.get_full_name()
            self.fields['email'].widget = forms.HiddenInput()
            self.fields['email'].initial = self.request.user.email

        if not defs.CONTACTWARE_DEFAULT_FROM_EMAIL:
            raise ValidationError(_("You need to set DEFAULT_FROM_EMAIL in your settings"))
        if not defs.CONTACTWARE_DEFAULT_TO_EMAILS:
            raise ValidationError(_("You need to set MANAGERS in your settings"))

        self.subject_template = defs.CONTACTWARE_MESSAGE_SUBJECT_TEMPLATE
        self.body_template = defs.CONTACTWARE_MESSAGE_BODY_TEMPLATE

        self.site = Site.objects.get_current()
        self.email_sent = False

    def get_message_subject(self):
        """
        Returns the rendered version of the message subject without linebreak.
        """
        subject = loader.render_to_string(self.subject_template, self.get_rendering_context())
        subject = ''.join(subject.splitlines())
        return subject

    def get_message_body(self):
        """
        Returns the rendered version of the message body.
        """
        body = loader.render_to_string(self.body_template, self.get_rendering_context())
        return body

    def get_message_dict(self):
        """
        Returns a dict with all required fields for the email to be sent out.
        """
        message_dict = {
            "subject": self.get_message_subject(),
            "message": self.get_message_body(),
            "from_email": defs.CONTACTWARE_DEFAULT_FROM_EMAIL,
            "recipient_list": defs.CONTACTWARE_DEFAULT_TO_EMAILS,
        }
        return message_dict

    def get_rendering_context(self):
        """
        Returns the context using which the subject/message is rendered.
        """
        extra_context = dict(self.cleaned_data, site=self.site, time=timezone.now())
        full_context = RequestContext(self.request, extra_context)
        return full_context

    def clean_email(self):
        """
        If email is valid.
        """
        email = self.cleaned_data['email']
        if not simple_email_re.match(email):
            raise forms.ValidationError(_('Invalid email address'))
        return email

    def save(self, fail_silently=False, commit=defs.CONTACTWARE_STORE_DB,
        send=defs.CONTACTWARE_SEND_EMAIL, subject_template=None, body_template=None,
        *args, **kwargs):
        """
        Send the email out if send flag is set, Save to DB if flag is Set.
        """
        if not self.email_sent and send:
            if subject_template is not None:
                self.subject_template = subject_template
            if body_template is not None:
                self.body_template = body_template
            send_mail(fail_silently=fail_silently, **self.get_message_dict())
            self.email_sent = True
        return super(ContactForm, self).save(commit, *args, **kwargs)

    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message', 'referrer', 'identifier',)
