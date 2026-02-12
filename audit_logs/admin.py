from django.contrib import admin

from clm_backend.admin_site import admin_site
from clm_backend.admin_utils import ReadOnlyAdminMixin, TenantScopedAdminMixin

from .models import AuditLogModel


@admin.register(AuditLogModel, site=admin_site)
class AuditLogAdmin(TenantScopedAdminMixin, ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        "created_at",
        "tenant_id",
        "user_id",
        "entity_type",
        "entity_id",
        "action",
        "ip_address",
    )
    list_filter = ("action", "entity_type", "created_at")
    search_fields = ("id", "tenant_id", "user_id", "entity_type", "entity_id", "ip_address")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    readonly_fields = (
        "id",
        "tenant_id",
        "user_id",
        "entity_type",
        "entity_id",
        "action",
        "changes",
        "ip_address",
        "created_at",
    )
