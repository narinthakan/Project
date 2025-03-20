# Generated by Django 5.1.6 on 2025-03-12 06:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0016_approvalrequest"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.CharField(
                choices=[
                    ("Cleansers", "คลีนซิ่ง"),
                    ("Toners", "โทนเนอร์"),
                    ("Serums", "เซรั่ม"),
                    ("Moisturizers", "มอยส์เจอไรเซอร์"),
                    ("Sunscreens", "ครีมกันแดด"),
                ],
                max_length=100,
            ),
        ),
    ]
