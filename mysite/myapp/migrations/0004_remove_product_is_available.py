# Generated by Django 5.1.4 on 2024-12-28 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_product_alter_user_avatar_purchase_return'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='is_available',
        ),
    ]
