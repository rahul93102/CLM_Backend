from rest_framework import serializers

from .models import CalendarEvent


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "tenant_id",
            "created_by",
            "title",
            "summary",
            "description",
            "start_datetime",
            "end_datetime",
            "all_day",
            "category",
            "associated_contract_id",
            "associated_contract_title",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "tenant_id",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        start = attrs.get("start_datetime") or getattr(self.instance, "start_datetime", None)
        end = attrs.get("end_datetime") or getattr(self.instance, "end_datetime", None)
        if start and end and end <= start:
            raise serializers.ValidationError({"end_datetime": "End datetime must be after start datetime."})
        return attrs
