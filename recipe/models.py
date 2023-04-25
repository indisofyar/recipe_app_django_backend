from django.db import models
from PIL import Image
from django.core.files import File
from django.db import models
from django.db.models import IntegerField, Model
from django.core.validators import MaxValueValidator, MinValueValidator
from io import BytesIO


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(null=True)
    is_selected = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}'


class Preferences(models.Model):
    name = models.CharField(max_length=255)
    amount = IntegerField(
        default=0,
        validators=[
            MaxValueValidator(7),
            MinValueValidator(0)
        ]
    )
    slug = models.SlugField(null=True)
    is_selected = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}'


class Recipe(models.Model):
    ingredients = models.TextField(null=True, blank=True)
    method = models.TextField(null=True, blank=True)
    time = models.CharField(max_length=255, default='')
    serves = models.IntegerField(null=True, blank=True)
    category = models.ManyToManyField(Category, related_name='recipe')
    preferences = models.ManyToManyField(Preferences, related_name='recipe')
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    image_external_url = models.URLField(max_length=255,null=True, blank=True)
    thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    url = models.URLField(max_length=255,null=True, blank=True)

    class Meta:
        ordering = ('-date_added',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}'

    def get_image(self):
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.url
        elif self.image_external_url:
            return self.image_external_url
        return ''

    def get_thumbnail(self):
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                return
            else:
                return ''

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)
        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


class Day(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    name = models.CharField(
        max_length=255,
        choices=DAY_CHOICES,
        default='MO',
    )
    is_selected = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    recipe = models.ForeignKey(
        Recipe, blank=True, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ('date_added',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}'


class MealSettings(models.Model):
    cuisines = models.ManyToManyField(Category, related_name='meal_settings')
    min_cook_minutes = IntegerField(
        default=10,
        validators=[
            MaxValueValidator(480),
            MinValueValidator(10)
        ]
    )
    max_cook_minutes = IntegerField(
        default=1,
        validators=[
            MaxValueValidator(480),
            MinValueValidator(10)
        ]
    )
    preferences = models.ManyToManyField(Preferences, related_name='meal_settings')