# Generated by Django 5.0.7 on 2024-09-02 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upstox_integration', '0004_profile_bio_profile_date_of_birth_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='date_of_birth',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='profile_picture',
        ),
        migrations.AddField(
            model_name='profile',
            name='dob',
            field=models.DateField(default='2000-01-01'),
        ),
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.CharField(default='Unknown', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(default='0000000000', max_length=15),
            preserve_default=False,
        ),
    ]
