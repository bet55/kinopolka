# Generated by Django 5.1.2 on 2025-06-17 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("postcard", "0005_alter_postcard_created_at"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="postcard",
            options={"ordering": ["-meeting_date"]},
        ),
        migrations.AlterField(
            model_name="postcard",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
