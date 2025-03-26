from django.db import migrations

from lists.models import User


def add_emails_to_users(apps, schema_editor):
    emails = {
        "drbloody1": "9261881@gmail.com",
        'daenillando': 'daenur.al@gmail.com',
        'lightthouse': 'darkpolarbear42@gmail.com',
        'Deputant': 'shulaev_2000@mail.ru'
    }
    try:
        users = User.objects.filter(email='').order_by('id')

        for user in users:
            user.email = emails.get(user.username)
            user.save()
    except Exception as e:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ('lists', '0003_remove_note_user_film_key_and_more'),
    ]

    operations = [
        migrations.RunPython(add_emails_to_users),
    ]
