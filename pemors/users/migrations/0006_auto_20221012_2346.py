# Generated by Django 3.2.15 on 2022-10-12 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_rating_counter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['rating_counter'], name='users_user_rating__437479_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['username'], name='users_user_usernam_65d164_idx'),
        ),
    ]
