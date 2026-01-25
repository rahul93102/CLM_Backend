from datetime import datetime, time

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import CalendarEvent
from .serializers import CalendarEventSerializer


def _parse_range_value(value: str):
    """Parse either an ISO datetime or YYYY-MM-DD into an aware datetime."""
    if not value:
        return None

    dt = parse_datetime(value)
    if dt is not None:
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt

    d = parse_date(value)
    if d is None:
        return None

    dt = datetime.combine(d, time.min)
    return timezone.make_aware(dt, timezone.get_current_timezone())


class CalendarEventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CalendarEventSerializer

    def get_queryset(self):
        user = self.request.user
        tenant_id = getattr(user, "tenant_id", None)
        user_id = getattr(user, "user_id", None)

        qs = CalendarEvent.objects.all()
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
        if user_id:
            qs = qs.filter(created_by=user_id)

        start = _parse_range_value(self.request.query_params.get("start", ""))
        end = _parse_range_value(self.request.query_params.get("end", ""))

        # Overlap filter: event intersects [start, end)
        if start and end:
            qs = qs.filter(start_datetime__lt=end, end_datetime__gte=start)

        return qs.order_by("start_datetime")

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(
            tenant_id=getattr(user, "tenant_id", None),
            created_by=getattr(user, "user_id", None),
        )
