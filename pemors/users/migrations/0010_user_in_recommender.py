# Generated by Django 3.2.15 on 2022-10-17 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20221015_2001'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='in_recommender',
            field=models.BooleanField(default=False),
        ),
    ]