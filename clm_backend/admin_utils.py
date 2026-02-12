from __future__ import annotations

import json
from typing import Any, Iterable

from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.http import HttpRequest
from django.utils.html import format_html


class ReadOnlyAdminMixin:
    """Make a ModelAdmin effectively read-only (viewable but not editable)."""

    def has_add_permission(self, request: HttpRequest) -> bool:  # type: ignore[override]
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:  # type: ignore[override]
        # Allow viewing the change form, but prevent saving.
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:  # type: ignore[override]
        return False


class TenantScopedAdminMixin:
    """Tenant-scoped queryset filtering for the Admin.

    Assumes one of:
    - a `tenant_id` UUIDField
    - a `tenant` FK with `id`

    Non-superusers are restricted to `request.user.tenant_id`.
    Superusers can see all; optionally filter dashboard/query by `?tenant=<uuid>`.
    """

    tenant_id_field_name = "tenant_id"
    tenant_fk_field_name = "tenant"

    def _effective_tenant_id(self, request: HttpRequest) -> str | None:
        if request.user.is_superuser:
            return request.GET.get("tenant") or None
        tenant_id = getattr(request.user, "tenant_id", None)
        return str(tenant_id) if tenant_id else None

    def get_queryset(self, request: HttpRequest):  # type: ignore[override]
        qs = super().get_queryset(request)
        tenant_id = self._effective_tenant_id(request)
        if not tenant_id:
            return qs
        model = qs.model
        field_names = {f.name for f in model._meta.get_fields()}
        if self.tenant_id_field_name in field_names:
            return qs.filter(**{self.tenant_id_field_name: tenant_id})
        if self.tenant_fk_field_name in field_names:
            return qs.filter(**{f"{self.tenant_fk_field_name}__id": tenant_id})
        return qs


def pretty_json(value: Any) -> str:
    try:
        return json.dumps(value, indent=2, sort_keys=True, cls=DjangoJSONEncoder)
    except Exception:
        return str(value)


class PrettyJSONAdminMixin:
    """Convenience helpers for rendering JSON fields nicely."""

    json_fields: Iterable[str] = ()

    def get_readonly_fields(self, request: HttpRequest, obj: Any | None = None):  # type: ignore[override]
        base = list(super().get_readonly_fields(request, obj))
        for field in self.json_fields:
            if field not in base:
                base.append(field)
        return base

    def formfield_for_dbfield(self, db_field: models.Field, request: HttpRequest, **kwargs: Any):  # type: ignore[override]
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in set(self.json_fields):
            try:
                formfield.widget.attrs.update({"style": "font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;"})
            except Exception:
                pass
        return formfield


def json_pre(value: Any) -> str:
    return format_html("<pre style='white-space: pre-wrap; max-width: 1000px;'>{}</pre>", pretty_json(value))
