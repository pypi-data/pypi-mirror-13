from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.sites.models import Site

from toolware.utils.mixin import CsrfProtectMixin

from .forms import ContactForm
from .models import ContactMessage
from . import signals


class ContactFormView(CsrfProtectMixin, CreateView):
    """
    Contact form view.
    """
    form_class = ContactForm
    model = ContactMessage
    template_name = 'contact/form.html'
    success_url = reverse_lazy('contactware:contactware_confirmation_view')

    def get_form_kwargs(self):
        kwargs = super(ContactFormView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        signals.contact_sent.send(sender=ContactMessage, request=self.request, contact=self.object)
        return super(ContactFormView, self).form_valid(form)

    def get_initial(self):
        initial = super(ContactFormView, self).get_initial().copy()
        initial['referrer'] = self.request.META.get('HTTP_REFERER', 'Unknown')
        if self.request.user.is_authenticated():
            initial['name'] = self.request.user.get_full_name()
            initial['email'] = self.request.user.email
        return initial


class ContactMessageSentView(TemplateView):
    """
    Message sent.
    """
    template_name = 'contact/confirmation.html'

    def get_context_data(self, **kwargs):
        context = super(ContactMessageSentView, self).get_context_data(**kwargs)
        current_site = Site.objects.get_current()
        context.update({
            "site": current_site,
        })
        return context
