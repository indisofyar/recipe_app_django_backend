from django.db.models import Q
from django.http import Http404, JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

import re
import json
import random
from bs4 import BeautifulSoup
import requests
import json
from .models import Recipe, Day, Category, Preferences
from .serializers import RecipeSerializer, DaySerializer, CategorySerializer, PreferencesSerializer

class LatestRecipeList(APIView):
    def get(self, request, format=None):
        recipes = Recipe.objects.all()[0:10]
        serializer = RecipeSerializer(
            recipes, many=True, context={'request': request})
        return Response(serializer.data)


class RecipeDetail(APIView):
    def get_object(self, recipe_slug):
        try:
            return Recipe.objectts.get(slug=recipe_slug)
        except Recipe.DoesNotExist:
            raise Http404

    def get(self, request, recipe_slug, format=None):
        recipe = self.get_object(recipe_slug)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)


class AllDays(APIView):
    def get(self, request, format=None):
        days = Day.objects.all()[0:7]
        serializer = DaySerializer(days, many=True)
        return Response(serializer.data)


class AllCuisines(APIView):
    def get(self, request, format=None):
        cuisines = Category.objects.all()[0:7]
        serializer = CategorySerializer(cuisines, many=True)
        return Response(serializer.data)


class AllPreferences(APIView):
    def get(self, request, format=None):
        preferences = Preferences.objects.all()[0:7]
        serializer = PreferencesSerializer(preferences, many=True)
        return Response(serializer.data)


class MealSettings(APIView):
    def get(self, request, format=None):
        preferences = Preferences.objects.all()[0:7]
        preferences_serializer = PreferencesSerializer(preferences, many=True)
        return Response(preferences_serializer.data)


@api_view(['POST'])
def search(request):
    query = request.data.get('query', '')
    if query:
        recipes = Recipe.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query))
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)
    else:
        return Response({'recipes': []})


@api_view(['POST'])
def set_day(request):
    day = request.data.get('day', '')
    recipe_id = request.data.get('id', '')
    day_to_set = Day.objects.get(name=day)
    day_to_set.recipe = Recipe.objects.get(pk=recipe_id)
    day_to_set.save()
    return Response('Day has been set')


@api_view(['DELETE'])
def delete_recipe(request):
    # Find any matching days and set their recipes to null
    days = Day.objects.filter(recipe__id=request.data.get('id', ''))
    for day in days:
        day.recipe = None
        day.save()
    recipe_id = request.data.get('id', '')
    recipe_to_delete = Recipe.objects.get(pk=recipe_id)
    recipe_to_delete.delete()
    return Response('Recipe deleted')


@api_view(['POST'])
def filter_recipes(request):
    query = request.data.get('query', '')
    if query:
        recipes = Recipe.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query))
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)
    else:
        return Response({'recipes': []})


@api_view(['POST'])
def get_recipe(request):
    url = request.data.get('url', '')
    recipe = {'name': '', 'ingredients': [], 'method': [],
              'time': '', 'serves': '', 'image': '', 'url': url}
    if url.startswith('https://www.bbcgoodfood.com/'):

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            recipe['name'] = soup.find('h1').text
            if not recipe['name'] or len(recipe['name']) < 1:
                return JsonResponse({'error': 'Not a valid BBC Good Food URL'})
            else:
                ingredients_list = soup.select(
                    '.recipe__ingredients ul li.list-item')
                for ingredient in ingredients_list:
                    # Trim string up to line break where ingredient anchor description starts
                    line_break = ingredient.text.find('\n')
                    if line_break > 0:
                        recipe['ingredients'].append(
                            ingredient.text[:line_break])
                    else:
                        recipe['ingredients'].append(ingredient.text)
                method_list = soup.select(
                    '.recipe__method-steps ul .list-item p')
                for step in method_list:
                    recipe['method'].append(step.text)
                try:
                    recipe['time']['prep'] = soup.select(
                        '.cook-and-prep-time .list time')[0].text
                    recipe['time']['cook'] = soup.select(
                        '.cook-and-prep-time .list time')[-1].text
                except:
                    pass
                recipe['serves'] = int(re.findall(
                    r'\d+', soup.select('.post-header__servings')[-1].text)[0])
                print(soup)
                recipe['image'] = soup.select(
                    '.post-header__image-container img')[0]['src']
                return JsonResponse(recipe)
        else:
            return JsonResponse({'error': 'Invalid URI'})
    elif url.startswith('https://www.bbc.co.uk/food/'):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tags = soup.select('script[type="application/ld+json"]')
            recipe_data = None
            for script in script_tags:
                script_json = json.loads(script.string)
                if script_json.get('@type') == 'Recipe':
                    recipe_data = script_json
                    break
            if not recipe_data:
                return JsonResponse({'error': 'Recipe not found'})
            recipe['name'] = recipe_data['name']
            recipe['ingredients'] = recipe_data['recipeIngredient']
            recipe['method'] = recipe_data['recipeInstructions']
            prep_time = parse_duration(recipe_data['prepTime'])
            cook_time = parse_duration(recipe_data['cookTime'])
            recipe['time']['prep'] = f"{prep_time.hours} hours " if prep_time.hours else ''
            recipe['time']['prep'] += f"{prep_time.minutes} minutes" if prep_time.minutes else ''
            recipe['time']['cook'] = f"{cook_time.hours} hours " if cook_time.hours else ''
            recipe['time']['cook'] += f"{cook_time.minutes} minutes" if cook_time.minutes else ''
            recipe['serves'] = int(re.findall(
                r'\d+', recipe_data['recipeYield'])[0])
            recipe['image'] = recipe_data['image'][0]
            return JsonResponse(recipe)
        else:
            return JsonResponse({'error': 'Invalid URI'})
    else:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                script_tags = soup.select('script[type="application/ld+json"]')
                recipe_data = None
                print(soup)
                for script in script_tags:
                    script_json = json.loads(script.string)
                    if script_json.get('@type') == 'Recipe':
                        recipe_data = script_json
                        break
                print(recipe_data)
                if not recipe_data:
                    return JsonResponse({'error': 'Recipe not found'})

                try:
                    recipe['name'] = recipe_data['name']
                except:
                    pass
                try:
                    recipe['ingredients'] = recipe_data['recipeIngredient']
                except:
                    pass
                try:
                    recipe['method'] = recipe_data['recipeInstructions']
                except:
                    pass
                try:
                    recipe['image'] = recipe_data['image']['url']
                except:
                    recipe['image'] = recipe_data['image']
                try:
                    recipe['serves'] = int(re.findall(
                        r'\d+', recipe_data['recipeYield'])[0])
                except:
                    recipe['serves'] = None
                try:
                    prep_time = parse_duration(recipe_data['prepTime'])
                    cook_time = parse_duration(recipe_data['cookTime'])
                    recipe['time'] = prep_time + cook_time
                except:
                    pass
                return JsonResponse(recipe)
        except:
            return JsonResponse({'error': 'Invalid URI'})


def parse_duration(duration_str):
    hours = 0
    minutes = 0
    duration_str = duration_str.upper()

    # Parse hours
    hours_index = duration_str.find("H")
    if hours_index >= 0:
        hours_str = duration_str[:hours_index]
        hours = int(hours_str)

    # Parse minutes
    minutes_index = duration_str.find("M")
    if minutes_index >= 0:
        if hours_index >= 0:
            minutes_str = duration_str[hours_index+1:minutes_index]
        else:
            minutes_str = duration_str[:minutes_index]
        minutes = int(minutes_str)  # Convert minutes string to integer

    return {"hours": hours, "minutes": minutes}


@api_view(['POST'])
def save_recipe(request):
    recipe = request.data.get('recipe', [])
    # Check if the recipe already exists within the database
    if Recipe.objects.filter(url=recipe['url']):
        return Response('This recipe already exists in the database')
    if recipe:
        new_recipe = Recipe()
        new_recipe.name = recipe['name']
        if type(recipe['image']) == str:
            new_recipe.image_external_url = recipe['image']
        else:
            new_recipe.image = recipe['image']
        new_recipe.url = recipe['url']
        if (isinstance(recipe['serves'], int)):
            new_recipe.serves = recipe['serves']
        new_recipe.time = recipe['time']
        new_recipe.ingredients = recipe['ingredients']
        new_recipe.method = recipe['method']
        new_recipe.save()
    return Response(False)


@api_view(['PUT'])
def toggle_selected_day(request):
    day = request.data.get('day', [])
    day_edit = Day.objects.get(id=day['id'])
    day_edit.is_selected = request.data['day']['is_selected']
    day_edit.save()
    return Response(day_edit.is_selected)


@api_view(['POST'])
def generate_recipes(request):

    # Get selected days
    days = Day.objects.filter(is_selected=True)
    not_selected = Day.objects.filter(is_selected=False)
    for day in not_selected:
        day.recipe = None
        day.save()
    recipes = Recipe.objects.all()
    # Generate an array of ids of preferenced recipes
    preferences = request.data.get('preferences', [])
    preferenced_recipes = set()
    for index, requested_preference in enumerate(preferences):
        qs = Recipe.objects.filter(
            preferences__name=requested_preference['name'])
        for recipe in qs:
            if recipe not in preferenced_recipes:
                preferenced_recipes.add(recipe)
    # Pad out the rest of recipes if needed
    index = 0
    while len(preferenced_recipes) < len(days) and index < len(recipes):
        preferenced_recipes.add(recipes[index])
        index += 1
    # Put recipes in days in a random order
    dayOrder = []
    while len(dayOrder) < len(days):
        random_number = random.randint(0, len(days) - 1)
        if random_number not in dayOrder:
            dayOrder.append(random_number)
    # Set days
    index = 0
    index_two = 0
    preferenced_recipes = list(preferenced_recipes)
    message = ''
    try:
        for randomNumber in dayOrder:
            days[randomNumber].recipe = Recipe.objects.get(
                id=preferenced_recipes[index_two].id)
            index_two += 1
            days[randomNumber].save()
        message = 'Recipes populated successfully'
    except IndexError:
        message = "There aren't enough unique recipes to fulfill this request"
    serializer = DaySerializer(days, many=True)
    return Response(message)
