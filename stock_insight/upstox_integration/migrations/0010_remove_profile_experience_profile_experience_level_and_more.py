# Generated by Django 5.0.7 on 2024-10-27 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upstox_integration', '0009_remove_profile_preferred_sectors_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='experience',
        ),
        migrations.AddField(
            model_name='profile',
            name='experience_level',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='trading_knowledge',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
