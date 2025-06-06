from django_filters import rest_framework
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientFilter(SearchFilter):
    """Фильтрация по ингридиентам."""

    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    """Фильтраци для рецептов."""

    tags = rest_framework.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        method='filter_tags'
    )
    is_favorited = rest_framework.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            tags__slug__in=value
        ).distinct()

    def filter_favorited(self, queryset, name, value):
        user = (
            self.request.user
            if self.request.user.is_authenticated
            else None
        )
        if value and user:
            return queryset.filter(favorite__user_id=user.id)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        user = (
            self.request.user
            if self.request.user.is_authenticated
            else None
        )
        if value and user:
            return queryset.filter(in_shopping_lists__user_id=user.id)
        return queryset
