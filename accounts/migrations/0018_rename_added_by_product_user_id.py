# Generated by Django 5.1.6 on 2025-03-16 11:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0017_alter_product_category"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="added_by",
            new_name="user_id",
        ),
    ]
