# Generated by Django 5.1 on 2024-11-08 06:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0007_profile_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="rating",
            field=models.DecimalField(decimal_places=1, max_digits=2, null=True),
        ),
    ]