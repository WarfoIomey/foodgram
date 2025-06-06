from django.contrib import admin

from .models import Tag, Recipe, Ingredients, Favorite, ShoppingList, RecipeIngredient, ShoppingListItem



@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Настройка админки для модели RecipeIngredient."""

    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe',)


@admin.register(ShoppingListItem)
class ShoppingListItemientAdmin(admin.ModelAdmin):
    """Настройка админки для модели ShoppingListItem."""

    list_display = ('id', 'shopping_list', 'ingredient', 'amount')
    search_fields = ('shopping_list',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка админки для модели Tag."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка админки для модели Ingredients."""

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка админки для модели Recipe."""

    list_display = (
        'id',
        'author',
        'name',
    )
    search_fields = ('name',)
    list_filter = ('author', 'tags')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройка админки для модели Favorite."""

    list_display = (
        'id',
        'user',
        'recipe',
    )
    list_filter = ('user', 'recipe')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Настройка админки для модели ShoppingList."""

    list_display = ('user',)
    search_fields = ('user',)
