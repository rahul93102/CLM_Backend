from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from django.apps import apps
from django.contrib.admin import AdminSite
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpRequest
from django.utils import timezone


def _month_start(d: date) -> date:
    return d.replace(day=1)


def _add_months(d: date, months: int) -> date:
    # Pure date arithmetic without external deps.
    month_index = (d.year * 12 + (d.month - 1)) + months
    year = month_index // 12
    month = (month_index % 12) + 1
    return date(year, month, 1)


def _last_n_month_starts(n: int, now: date | None = None) -> list[date]:
    now = now or timezone.now().date()
    end = _month_start(now)
    starts = [_add_months(end, -i) for i in reversed(range(n))]
    return starts


def _bucket_month_counts(qs, dt_field: str, month_starts: list[date]) -> dict[str, Any]:
    start_dt = datetime.combine(month_starts[0], datetime.min.time(), tzinfo=timezone.get_current_timezone())

    rows = (
        qs.filter(**{f"{dt_field}__gte": start_dt})
        .annotate(month=TruncMonth(dt_field))
        .values("month")
        .annotate(count=Count("pk"))
        .order_by("month")
    )
    row_map = {r["month"].date().replace(day=1): int(r["count"]) for r in rows if r.get("month")}

    labels = [ms.strftime("%b %Y") for ms in month_starts]
    series = [row_map.get(ms, 0) for ms in month_starts]
    return {"labels": labels, "series": series}


def _tenant_filter_kwargs(model, tenant_id: str) -> dict[str, Any] | None:
    try:
        field_names = {f.name for f in model._meta.get_fields()}
    except Exception:
        return None
    if "tenant_id" in field_names:
        return {"tenant_id": tenant_id}
    if "tenant" in field_names:
        return {"tenant__id": tenant_id}
    return None


def _get_model(app_label: str, model_name: str):
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


class CLMAdminSite(AdminSite):
    site_header = "CLM Governance"
    site_title = "CLM Admin"
    index_title = "Governance Dashboard"
    index_template = "admin/dashboard_index.html"

    def _effective_tenant_filter(self, request: HttpRequest) -> Q:
        if request.user.is_superuser:
            tenant = request.GET.get("tenant")
            if tenant:
                return Q(tenant_id=tenant) | Q(tenant__id=tenant)  # model-dependent
            return Q()
        tenant_id = getattr(request.user, "tenant_id", None)
        if tenant_id:
            return Q(tenant_id=str(tenant_id)) | Q(tenant__id=str(tenant_id))
        return Q()

    def index(self, request: HttpRequest, extra_context: dict[str, Any] | None = None):  # type: ignore[override]
        extra_context = dict(extra_context or {})

        tenant_filter = self._effective_tenant_filter(request)
        effective_tenant_id = (
            request.GET.get("tenant")
            if request.user.is_superuser
            else (str(getattr(request.user, "tenant_id", "") or "") or None)
        )

        month_starts = _last_n_month_starts(12)
        now = timezone.now()
        last_30 = now - timedelta(days=30)

        User = _get_model("authentication", "User")
        Document = _get_model("repository", "Document")
        SearchAnalytics = _get_model("search", "SearchAnalyticsModel")
        Contract = _get_model("contracts", "Contract")
        ContractTemplate = _get_model("contracts", "ContractTemplate")
        WorkflowInstance = _get_model("workflows", "WorkflowInstance")
        DraftTask = _get_model("ai", "DraftGenerationTask")
        OCRJob = _get_model("ocr", "OCRJobModel")
        RedactionJob = _get_model("redaction", "RedactionJobModel")
        ReviewContract = _get_model("reviews", "ReviewContract")

        # Time-series
        users_series = {"labels": [], "series": []}
        uploads_series = {"labels": [], "series": []}
        searches_series = {"labels": [], "series": []}

        if User is not None:
            users_series = _bucket_month_counts(User.objects.filter(tenant_filter), "date_joined", month_starts)

        if Document is not None:
            uploads_series = _bucket_month_counts(Document.objects.filter(tenant_filter), "uploaded_at", month_starts)

        if SearchAnalytics is not None:
            searches_series = _bucket_month_counts(SearchAnalytics.objects.filter(tenant_filter), "created_at", month_starts)

        # Month-wise feature usage
        feature_usage_monthly = {
            "labels": [ms.strftime("%b %Y") for ms in month_starts],
            "series": [],
        }
        feature_defs: list[tuple[str, Any, str, dict[str, Any] | None]] = []

        Approval = _get_model("approvals", "ApprovalModel")
        Notification = _get_model("notifications", "NotificationModel")
        CalendarEvent = _get_model("calendar_events", "CalendarEvent")

        if Contract is not None:
            feature_defs.append(("Contracts", Contract, "created_at", _tenant_filter_kwargs(Contract, effective_tenant_id) if effective_tenant_id else None))
        if ContractTemplate is not None:
            feature_defs.append(("Templates", ContractTemplate, "created_at", _tenant_filter_kwargs(ContractTemplate, effective_tenant_id) if effective_tenant_id else None))
        if Document is not None:
            feature_defs.append(("Uploads", Document, "uploaded_at", _tenant_filter_kwargs(Document, effective_tenant_id) if effective_tenant_id else None))
        if SearchAnalytics is not None:
            feature_defs.append(("Search", SearchAnalytics, "created_at", _tenant_filter_kwargs(SearchAnalytics, effective_tenant_id) if effective_tenant_id else None))
        if WorkflowInstance is not None:
            # WorkflowInstance doesn't have tenant_id; scope via workflow.
            wf_kw = {"workflow__tenant_id": effective_tenant_id} if effective_tenant_id else None
            feature_defs.append(("Workflows", WorkflowInstance, "created_at", wf_kw))
        if Approval is not None:
            feature_defs.append(("Approvals", Approval, "created_at", _tenant_filter_kwargs(Approval, effective_tenant_id) if effective_tenant_id else None))
        if Notification is not None:
            feature_defs.append(("Notifications", Notification, "created_at", _tenant_filter_kwargs(Notification, effective_tenant_id) if effective_tenant_id else None))
        if CalendarEvent is not None:
            feature_defs.append(("Calendar", CalendarEvent, "created_at", _tenant_filter_kwargs(CalendarEvent, effective_tenant_id) if effective_tenant_id else None))
        if DraftTask is not None:
            feature_defs.append(("AI Drafts", DraftTask, "created_at", _tenant_filter_kwargs(DraftTask, effective_tenant_id) if effective_tenant_id else None))
        if OCRJob is not None:
            feature_defs.append(("OCR", OCRJob, "created_at", _tenant_filter_kwargs(OCRJob, effective_tenant_id) if effective_tenant_id else None))
        if RedactionJob is not None:
            feature_defs.append(("Redaction", RedactionJob, "created_at", _tenant_filter_kwargs(RedactionJob, effective_tenant_id) if effective_tenant_id else None))
        if ReviewContract is not None:
            feature_defs.append(("Review", ReviewContract, "created_at", _tenant_filter_kwargs(ReviewContract, effective_tenant_id) if effective_tenant_id else None))

        # Keep chart readable: take top 8 by total usage over the window.
        computed: list[dict[str, Any]] = []
        for name, model, dt_field, kw in feature_defs:
            try:
                qs = model.objects.all()
                if kw:
                    qs = qs.filter(**kw)
                bucketed = _bucket_month_counts(qs, dt_field, month_starts)
                total = sum(bucketed["series"]) if bucketed.get("series") else 0
                computed.append({"name": name, "data": bucketed["series"], "total": total})
            except Exception:
                continue
        computed.sort(key=lambda x: x.get("total", 0), reverse=True)
        feature_usage_monthly["series"] = [{"name": c["name"], "data": c["data"]} for c in computed[:8]]

        # Feature breakdown (last 30d)
        def _count(model, field: str = "created_at") -> int:
            if model is None:
                return 0
            if field not in {f.name for f in model._meta.get_fields()}:
                return 0
            return model.objects.filter(tenant_filter).filter(**{f"{field}__gte": last_30}).count()

        feature_breakdown = {
            "Contracts": _count(Contract, "created_at"),
            "Uploads": _count(Document, "uploaded_at"),
            "Search": _count(SearchAnalytics, "created_at"),
            "Workflows": _count(WorkflowInstance, "created_at"),
            "AI Drafts": _count(DraftTask, "created_at"),
            "OCR": _count(OCRJob, "created_at"),
            "Redaction": _count(RedactionJob, "created_at"),
            "Review": _count(ReviewContract, "created_at"),
        }

        # AI adoption: percentage of tenants/users that started >=1 AI draft in last 30d.
        ai_adoption_pct = 0
        if DraftTask is not None and User is not None:
            tenant_ids = (
                DraftTask.objects.filter(tenant_filter)
                .filter(created_at__gte=last_30)
                .values_list("tenant_id", flat=True)
                .distinct()
            )
            total_tenants = 0
            TenantModel = _get_model("tenants", "TenantModel")
            if TenantModel is not None:
                total_tenants = TenantModel.objects.filter(tenant_filter).count() or 0
            if total_tenants:
                ai_adoption_pct = int(round((len(list(tenant_ids)) / total_tenants) * 100))
            else:
                # Fallback to users, if tenant model not present/loaded
                total_users = User.objects.filter(tenant_filter).count() or 0
                if total_users:
                    ai_users = (
                        DraftTask.objects.filter(tenant_filter)
                        .filter(created_at__gte=last_30)
                        .values_list("user_id", flat=True)
                        .distinct()
                    )
                    ai_adoption_pct = int(round((len(list(ai_users)) / total_users) * 100))

        # Popular templates
        popular_templates: list[dict[str, Any]] = []
        if ContractTemplate is not None:
            try:
                templates = (
                    ContractTemplate.objects.filter(tenant_filter)
                    .annotate(contracts_count=Count("contracts"))
                    .order_by("-contracts_count", "-created_at")[:5]
                )
                for t in templates:
                    popular_templates.append(
                        {
                            "name": getattr(t, "name", ""),
                            "type": getattr(t, "contract_type", ""),
                            "count": int(getattr(t, "contracts_count", 0) or 0),
                        }
                    )
            except Exception:
                pass

        dashboard = {
            "totals": {
                "users": int(User.objects.filter(tenant_filter).count()) if User is not None else 0,
                "uploads": int(Document.objects.filter(tenant_filter).count()) if Document is not None else 0,
                "searches": int(SearchAnalytics.objects.filter(tenant_filter).count()) if SearchAnalytics is not None else 0,
            },
            "series": {
                "users": users_series,
                "uploads": uploads_series,
                "searches": searches_series,
                "feature_usage": feature_usage_monthly,
            },
            "feature_breakdown": feature_breakdown,
            "ai_adoption_pct": ai_adoption_pct,
            "popular_templates": popular_templates,
        }

        extra_context["dashboard"] = dashboard
        extra_context["dashboard_tenant"] = request.GET.get("tenant") if request.user.is_superuser else str(getattr(request.user, "tenant_id", "") or "")

        return super().index(request, extra_context=extra_context)


admin_site = CLMAdminSite(name="clm_admin")
