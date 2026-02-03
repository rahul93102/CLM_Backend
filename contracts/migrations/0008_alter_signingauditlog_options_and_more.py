"""Firma follow-up indexes.

This migration intentionally avoids touching SignNow models. The originally
auto-generated file contained unintended operations caused by a temporary local
model inconsistency during development.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contracts", "0007_firma_esign_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="firmasigningauditlog",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AddIndex(
            model_name="firmasigningauditlog",
            index=models.Index(
                fields=["firma_signature_contract", "created_at"],
                name="firma_audit_sc_created_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="firmasigningauditlog",
            index=models.Index(
                fields=["event", "created_at"],
                name="firma_audit_event_created_idx",
            ),
        ),
    ]
