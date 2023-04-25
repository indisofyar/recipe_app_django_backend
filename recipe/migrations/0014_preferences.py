# Generated by Django 4.1.7 on 2023-03-21 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0013_category_is_selected'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(null=True)),
                ('is_selected', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]