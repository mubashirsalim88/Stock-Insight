# Generated by Django 5.0.7 on 2024-11-01 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upstox_integration', '0014_portfolio_transaction'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='timestamp',
            new_name='date',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='action',
            field=models.CharField(max_length=4),
        ),
    ]
