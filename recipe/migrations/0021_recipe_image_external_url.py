# Generated by Django 4.1.7 on 2023-03-29 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0020_recipe_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image_external_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]
