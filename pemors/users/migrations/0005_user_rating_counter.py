# Generated by Django 3.2.15 on 2022-10-12 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_profile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='rating_counter',
            field=models.IntegerField(default=0),
        ),
    ]