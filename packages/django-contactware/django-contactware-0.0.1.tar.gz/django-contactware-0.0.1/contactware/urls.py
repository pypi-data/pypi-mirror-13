from django.conf import settings
from django.conf.urls import url
from django.conf.urls import patterns

from .views import *


urlpatterns = [

    url(
        r'sent$',
        ContactMessageSentView.as_view(),
        name='contactware_confirmation_view',
    ),

    url(
        r'',
        ContactFormView.as_view(),
        name='contactware_form_view',
    ),

]
