# Generated by Django 3.2.15 on 2022-10-17 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_user_in_recommender'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['in_recommender'], name='users_user_in_reco_625bad_idx'),
        ),
    ]
