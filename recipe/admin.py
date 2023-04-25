from django.contrib import admin

from .models import Category, Recipe, Day,Preferences
# Register your models here.

admin.site.register(Category)
admin.site.register(Recipe)
admin.site.register(Day)
admin.site.register(Preferences)
