# Generated by Django 4.1.7 on 2023-03-29 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0019_recipe_ingredients_recipe_method_recipe_serves_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]
