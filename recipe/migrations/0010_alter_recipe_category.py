# Generated by Django 4.1.7 on 2023-03-20 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0009_remove_recipe_category_recipe_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='category',
            field=models.ManyToManyField(related_name='recipe', to='recipe.category'),
        ),
    ]
