# Generated by Django 3.2.15 on 2022-10-12 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titles', '0003_userrating_titles_user_user_id_805ebb_idx'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='userrating',
            index=models.Index(fields=['user'], name='titles_user_user_id_89606f_idx'),
        ),
        migrations.AddIndex(
            model_name='userrating',
            index=models.Index(fields=['title'], name='titles_user_title_i_e16030_idx'),
        ),
    ]
