from django.contrib import admin

from clm_backend.admin_site import admin_site

from .models import TenantModel


@admin.register(TenantModel, site=admin_site)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "status", "subscription_plan", "created_at", "updated_at")
    list_filter = ("status", "subscription_plan")
    search_fields = ("name", "domain")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")

    actions = ("activate_tenants", "deactivate_tenants", "suspend_tenants")

    @admin.action(description="Set status: active")
    def activate_tenants(self, request, queryset):
        queryset.update(status="active")

    @admin.action(description="Set status: inactive")
    def deactivate_tenants(self, request, queryset):
        queryset.update(status="inactive")

    @admin.action(description="Set status: suspended")
    def suspend_tenants(self, request, queryset):
        queryset.update(status="suspended")
