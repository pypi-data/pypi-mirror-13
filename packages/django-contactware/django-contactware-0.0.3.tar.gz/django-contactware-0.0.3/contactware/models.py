from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MinLengthValidator
from django.core.validators import MaxLengthValidator
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class ContactMessage(models.Model):
    """
    Contact Message Model
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(
        _("Your name"),
        max_length=120,
        blank=False,
    )

    email = models.EmailField(
        _('Your email address'),
        max_length=250,
        blank=False,
    )

    subject = models.CharField(
        _("Message Subject"),
        max_length=120,
        blank=False,
    )

    message = models.TextField(
        _('Your message'),
        blank=False,
        validators=[MinLengthValidator(10), MaxLengthValidator(750)],
    )

    referrer = models.CharField(
        _('referrer'),
        max_length=254,
        blank=True
    )

    identifier = models.CharField(
        _('Identifier'),
        max_length=15,
        blank=True
    )

    def __str__(self):
        return '{}-{}'.format(self.name, self.email)
