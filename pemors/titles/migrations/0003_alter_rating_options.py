# Generated by Django 4.0.5 on 2022-07-31 15:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0002_userrating'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rating',
            options={'ordering': ['-average_rating']},
        ),
    ]
