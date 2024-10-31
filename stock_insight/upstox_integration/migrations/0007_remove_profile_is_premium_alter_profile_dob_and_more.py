# Generated by Django 5.0.7 on 2024-09-23 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upstox_integration', '0006_alter_profile_dob'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='is_premium',
        ),
        migrations.AlterField(
            model_name='profile',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]