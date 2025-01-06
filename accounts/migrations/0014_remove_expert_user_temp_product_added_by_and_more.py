# Generated by Django 5.1.1 on 2025-01-05 18:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0013_skinupload"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="expert",
            name="user_temp",
        ),
        migrations.AddField(
            model_name="product",
            name="added_by",
            field=models.CharField(
                choices=[
                    ("Admin", "Admin"),
                    ("Expert", "Expert"),
                    ("Seller", "Seller"),
                ],
                default="Admin",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="role",
            field=models.CharField(
                choices=[
                    ("User", "User"),
                    ("Member", "Member"),
                    ("Admin", "Admin"),
                    ("Expert", "Expert"),
                    ("Seller", "Seller"),
                ],
                default="User",
                max_length=10,
            ),
        ),
    ]