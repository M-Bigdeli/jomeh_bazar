# Generated by Django 5.1.3 on 2025-01-03 08:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_category_productattribute_productattributevalue'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productattribute',
            name='category',
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='product.category'),
            preserve_default=False,
        ),
    ]
