# Generated by Django 5.1.2 on 2025-03-26 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("postcard", "0003_postcard_background_picture_postcard_is_active_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="postcard",
            old_name="background_picture",
            new_name="screenshot",
        ),
        migrations.AddField(
            model_name="postcard",
            name="title",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
