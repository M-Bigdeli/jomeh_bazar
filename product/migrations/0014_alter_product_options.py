# Generated by Django 5.1.4 on 2025-01-05 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_product_discount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-created_at']},
        ),
    ]
