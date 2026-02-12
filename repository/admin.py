from django.contrib import admin
from django.utils.html import format_html

from clm_backend.admin_site import admin_site
from clm_backend.admin_utils import ReadOnlyAdminMixin, TenantScopedAdminMixin, pretty_json

from .models import Document, DocumentChunk, DocumentMetadata, RepositoryFolderModel, RepositoryModel


class DocumentMetadataInline(ReadOnlyAdminMixin, admin.StackedInline):
    model = DocumentMetadata
    can_delete = False
    extra = 0
    fk_name = "document"

    readonly_fields = (
        "parties",
        "contract_value",
        "currency",
        "effective_date",
        "expiration_date",
        "identified_clauses",
        "obligations",
        "risk_score",
        "high_risk_items",
        "summary",
        "extracted_at",
        "updated_at",
    )


@admin.register(Document, site=admin_site)
class DocumentAdmin(TenantScopedAdminMixin, admin.ModelAdmin):
    list_display = (
        "filename",
        "document_type",
        "status",
        "tenant",
        "uploaded_by",
        "file_size",
        "uploaded_at",
        "processed_at",
    )
    list_filter = ("status", "document_type", "uploaded_at")
    search_fields = ("id", "filename", "r2_key")
    date_hierarchy = "uploaded_at"
    ordering = ("-uploaded_at",)
    list_select_related = ("tenant", "uploaded_by")

    inlines = (DocumentMetadataInline,)

    readonly_fields = (
        "id",
        "tenant",
        "uploaded_by",
        "filename",
        "file_type",
        "file_size",
        "r2_key",
        "document_type",
        "status",
        "processing_error",
        "full_text",
        "extracted_metadata_pretty",
        "uploaded_at",
        "processed_at",
        "updated_at",
    )

    fields = (
        "id",
        ("tenant", "uploaded_by"),
        ("filename", "file_type"),
        ("document_type", "status"),
        "file_size",
        "r2_key",
        "processing_error",
        "extracted_metadata_pretty",
        "full_text",
        ("uploaded_at", "processed_at", "updated_at"),
    )

    actions = ("retry_processing",)

    def extracted_metadata_pretty(self, obj: Document):
        return format_html(
            "<pre style='white-space: pre-wrap; max-width: 1000px;'>{}</pre>",
            pretty_json(obj.extracted_metadata),
        )

    extracted_metadata_pretty.short_description = "Extracted metadata"

    @admin.action(description="Retry processing (set status=uploaded, clear error)")
    def retry_processing(self, request, queryset):
        queryset.update(status="uploaded", processing_error=None)


@admin.register(DocumentChunk, site=admin_site)
class DocumentChunkAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("document", "chunk_number", "tenant", "is_processed", "created_at")
    list_filter = ("is_processed", "created_at")
    search_fields = ("id", "document__id", "document__filename")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("document", "tenant")


@admin.register(DocumentMetadata, site=admin_site)
class DocumentMetadataAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("document", "tenant", "risk_score", "effective_date", "expiration_date", "updated_at")
    list_filter = ("updated_at",)
    search_fields = ("document__filename", "document__id", "tenant__name")
    ordering = ("-updated_at",)
    list_select_related = ("document", "tenant")


@admin.register(RepositoryModel, site=admin_site)
class RepositoryModelAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("name", "document_type", "mime_type", "file_size", "tenant_id", "created_at")
    list_filter = ("document_type", "mime_type", "created_at")
    search_fields = ("id", "tenant_id", "name", "file_path")
    ordering = ("-created_at",)


@admin.register(RepositoryFolderModel, site=admin_site)
class RepositoryFolderAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("name", "tenant_id", "parent_id", "created_at")
    list_filter = ("created_at",)
    search_fields = ("id", "tenant_id", "name", "parent_id")
    ordering = ("-created_at",)
