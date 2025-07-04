# Generated by Django 5.0.3 on 2025-06-29 16:15

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('happ', '0010_alter_doctor_unique_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='journalentry',
            name='date',
        ),
        migrations.RemoveField(
            model_name='journalentry',
            name='details',
        ),
        migrations.AddField(
            model_name='journalentry',
            name='breath',
            field=models.CharField(default='No Data', max_length=255),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='chest_pain',
            field=models.CharField(default='No Data', max_length=255),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='emergency',
            field=models.CharField(default='No Data', max_length=255),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='energy_level',
            field=models.CharField(default='No Data', max_length=255),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='extra_note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='pain_level',
            field=models.CharField(default='No Data', max_length=255),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='physical_activity',
            field=models.CharField(default='No Data', max_length=255),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='stress_level',
            field=models.CharField(default='No Data', max_length=255),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='swelling',
            field=models.CharField(default='No Data', max_length=255),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
