# Generated by Django 5.1.4 on 2025-01-03 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_category_slug_alter_category_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70)),
                ('hex_code', models.CharField(max_length=7)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.ManyToManyField(related_name='product', to='product.color'),
        ),
    ]
