# Generated by Django 4.1.7 on 2023-03-21 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0012_category_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_selected',
            field=models.BooleanField(default=False),
        ),
    ]