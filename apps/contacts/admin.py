from django.contrib import admin
from config.admin import admin_site

from apps.contacts.models import Contact


class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "message", "status")
    list_editable = ("status",)
    list_display_links = ("id", "name")
    list_filter = ("status",)
    search_fields = ("name", "email", "message")
    ordering = ("-id",)


admin_site.register(Contact, ContactAdmin)
