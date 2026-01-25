import uuid

from django.db import models


class CalendarEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant_id = models.UUIDField(db_index=True)
    created_by = models.UUIDField(db_index=True)

    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")

    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField(db_index=True)
    all_day = models.BooleanField(default=False)

    CATEGORY_RENEWAL = "renewal"
    CATEGORY_EXPIRY = "expiry"
    CATEGORY_MEETING = "meeting"

    category = models.CharField(
        max_length=32,
        choices=[
            (CATEGORY_RENEWAL, "Renewal"),
            (CATEGORY_EXPIRY, "Expiry"),
            (CATEGORY_MEETING, "Meeting"),
        ],
        default=CATEGORY_MEETING,
    )

    associated_contract_id = models.UUIDField(null=True, blank=True, db_index=True)
    associated_contract_title = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calendar_events"
        indexes = [
            models.Index(
                fields=["tenant_id", "created_by", "start_datetime"],
                name="calendar_ev_tenant__517d13_idx",
            ),
            models.Index(
                fields=["tenant_id", "created_by", "end_datetime"],
                name="calendar_ev_tenant__7da475_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.start_datetime} -> {self.end_datetime})"
