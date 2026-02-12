from django.contrib import admin

from clm_backend.admin_site import admin_site
from clm_backend.admin_utils import ReadOnlyAdminMixin, TenantScopedAdminMixin

from .models import SearchIndexModel, SearchAnalyticsModel


@admin.register(SearchIndexModel, site=admin_site)
class SearchIndexAdmin(TenantScopedAdminMixin, ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("entity_type", "title", "tenant_id", "created_at", "updated_at")
    list_filter = ("entity_type", "created_at")
    search_fields = ("id", "tenant_id", "entity_id", "title", "content")
    date_hierarchy = "created_at"
    ordering = ("-updated_at",)

    readonly_fields = (
        "id",
        "tenant_id",
        "entity_type",
        "entity_id",
        "title",
        "content",
        "keywords",
        "metadata",
        "search_vector",
        "created_at",
        "updated_at",
        "indexed_at",
    )


@admin.register(SearchAnalyticsModel, site=admin_site)
class SearchAnalyticsAdmin(TenantScopedAdminMixin, ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("created_at", "tenant_id", "user_id", "query_type", "query", "results_count", "response_time_ms")
    list_filter = ("query_type", "created_at")
    search_fields = ("id", "tenant_id", "user_id", "query", "clicked_result_id", "clicked_result_type")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    readonly_fields = (
        "id",
        "tenant_id",
        "user_id",
        "query",
        "query_type",
        "results_count",
        "response_time_ms",
        "clicked_result_id",
        "clicked_result_type",
        "created_at",
    )
