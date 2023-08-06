from django.contrib import admin

from .models import ContactMessage


class ContactMessageAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'name',
        'email',
        'subject',
        'message',
        'identifier',
        'referrer',
        'updated_at',
        'created_at',
    ]

    search_fields = [
        'name',
        'email',
    ]

    list_per_page = 25

admin.site.register(ContactMessage, ContactMessageAdmin)
