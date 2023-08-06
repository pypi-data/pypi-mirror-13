import datetime
from django.utils import timezone

from .models import ContactMessage
from . import defaults as defs


def check_email(email, from_host, from_email):
    """ Check the existance of an email address by contacting the provider """

    exists = True
    if not defs.CONTACTWARE_VERIFY_EMAIL:
        return exists

    try:
        from spamware.email_check import email_exists
    except:
        return exists

    exists = email_exists(email, from_host, from_email)
    return exists


def check_spam(request, name, email, message):
    """ Check if the content is spam """

    spam = False
    if not defs.CONTACTWARE_VERIFY_SPAM:
        return spam

    try:
        from spamware.spam_check import check_spam
    except:
        return spam

    spam = check_spam(request, name, email, message)
    return spam


def clean_expired_contacts():
    """ Remove the expired contact messages from the database """

    expiration_date = datetime.timedelta(days=defs.CONTACTWARE_EXPIRY_DAYS)
    contacts = ContactMessage.objects.all()
    for contact in contacts:
        if contact.created_at + expiration_date < timezone.now():
            contact.delete()
