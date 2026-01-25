from django.contrib import admin

from .models import CalendarEvent


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "start_datetime", "end_datetime", "tenant_id", "created_by")
    list_filter = ("category",)
    search_fields = ("title", "summary", "description", "associated_contract_title")
