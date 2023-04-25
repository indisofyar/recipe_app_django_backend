from rest_framework import serializers
from .models import Category, Recipe, Day, Preferences

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "is_selected",
        )

class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = (
            "name",
            "amount"
        )

class RecipeSerializer(serializers.ModelSerializer):
    category = CategorySerializer(allow_null=True)
    preferences = PreferencesSerializer(many=True)
    class Meta:
        model = Recipe
        fields = (
            "pk",
            "name",
            "time",
            "serves",
            "ingredients",
            "get_image",
            "get_absolute_url",
            "category",
            "url",
            "preferences"
        )



class DaySerializer(serializers.Serializer):
    name = serializers.CharField()
    is_selected = serializers.BooleanField()
    recipe = RecipeSerializer(allow_null=True) # nested serializer for Recipe object
    id = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        return Day.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.is_selected = validated_data.get('is_selected', instance.is_selected)
        instance.recipe = validated_data.get('recipe', instance.recipe)
        instance.save()
        return instance

