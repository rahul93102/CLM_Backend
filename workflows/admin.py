from django.contrib import admin

from clm_backend.admin_site import admin_site
from clm_backend.admin_utils import TenantScopedAdminMixin

from .models import Workflow, WorkflowInstance


@admin.register(Workflow, site=admin_site)
class WorkflowAdmin(TenantScopedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "workflow_type", "status", "tenant_id", "created_by", "created_at", "updated_at")
    list_filter = ("status", "workflow_type", "created_at")
    search_fields = ("id", "tenant_id", "name", "description")
    date_hierarchy = "created_at"
    ordering = ("-updated_at",)

    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(WorkflowInstance, site=admin_site)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ("id", "workflow", "entity_type", "entity_id", "status", "current_step", "created_at", "updated_at")
    list_filter = ("status", "entity_type", "created_at")
    search_fields = ("id", "entity_id", "entity_type", "workflow__name")
    date_hierarchy = "created_at"
    ordering = ("-updated_at",)
    list_select_related = ("workflow",)

    readonly_fields = ("id", "created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            tenant = request.GET.get("tenant")
            if tenant:
                return qs.filter(workflow__tenant_id=tenant)
            return qs
        tenant_id = getattr(request.user, "tenant_id", None)
        if tenant_id:
            return qs.filter(workflow__tenant_id=str(tenant_id))
        return qs
