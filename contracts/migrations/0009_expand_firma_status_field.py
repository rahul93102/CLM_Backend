# Generated migration to expand FirmaSignatureContract.status field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contracts", "0008_alter_signingauditlog_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="firmasignaturecontract",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("sent", "Sent for Signature"),
                    ("in_progress", "In Progress"),
                    ("completed", "Completed"),
                    ("declined", "Declined"),
                    ("failed", "Failed"),
                ],
                db_index=True,
                default="draft",
                max_length=50,  # Expanded from 20 to 50
            ),
        ),
    ]
