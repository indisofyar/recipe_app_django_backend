from django.urls import path, include
from recipe import views

urlpatterns = [
    path('latest-recipes/', views.LatestRecipeList.as_view()),
    path('recipe/<slug:product_slug>', views.RecipeDetail.as_view()),
    path('all-days', views.AllDays.as_view()),
    path('recipes/search/', views.search),
    path('cuisines/', views.AllCuisines.as_view()),
    path('meal-settings/', views.MealSettings.as_view()),
    path('all-preferences/', views.AllPreferences.as_view()),
    path('generate-recipes/', views.generate_recipes),
    path('get-recipe/', views.get_recipe),
    path('save-recipe/', views.save_recipe),
    path('set-day/', views.set_day),
    path('toggle-selected-day/', views.toggle_selected_day),
    path('delete-recipe/', views.delete_recipe),
]
