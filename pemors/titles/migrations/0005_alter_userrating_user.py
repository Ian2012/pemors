# Generated by Django 3.2.15 on 2022-10-12 23:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('titles', '0004_auto_20221012_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='users.user'),
        ),
    ]
