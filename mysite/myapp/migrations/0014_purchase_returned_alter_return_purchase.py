# Generated by Django 5.1.4 on 2025-01-05 20:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_alter_user_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='returned',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='return',
            name='purchase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.purchase'),
        ),
    ]
