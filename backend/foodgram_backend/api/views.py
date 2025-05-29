from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from recipes.models import Tag, Recipe, Ingredients, Favorite, ShoppingList
from users.models import Follow
from .persmissions import IsAdminAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    TagSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    FavoriteSerializer,
    FollowSerializer,
    UserSerializer,
    ShortLinkSerializer,
    ShoppingCartSerializer,
)


User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination
    http_method_names = ['get']


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = PageNumberPagination
    http_method_names = ['get']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAdminAuthorOrReadOnly],
        serializer_class=FavoriteSerializer,
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        """PUT: добавление рецепта в избранное. DELETE: удаление."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = self.get_serializer(
                data={},
                context={
                    'request': request,
                    'recipe': recipe,
                },
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(
                user=self.request.user,
                recipe=recipe,
            )
            return Response(serializer.data)
        elif request.method == 'DELETE':
            try:
                favorite = Favorite.objects.get(
                    user=self.request.user,
                    recipe=recipe,
                )
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response(
                    {"error": "Рецепта нет в избранном"},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=True, methods=['get'], url_path='get-link')
    def generate_short_link(self, request, pk=None):
        recipe = self.get_object()
        serializer = ShortLinkSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def added_recipe(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        shopp_cart, created = ShoppingList.objects.get_or_create(
            user=request.user
        )
        shopp_cart.recipes.add(recipe)
        serializer = ShoppingCartSerializer(shopp_cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        if self.action == 'subscriptions':
            return Follow.objects.filter(user=self.request.user)
        return super().get_queryset()

    @action(
        methods=['get'],
        detail=False, url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def get_me(self, request):
        """Получение текущего пользователя."""
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        permission_classes=[IsAdminAuthorOrReadOnly]
    )
    def avatar(self, request):
        """PUT: добавление аватара, DELETE: удаление аватара."""
        user = request.user
        if request.method == "PUT":
            serializer = AvatarSerializer(
                instance=user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if request.method == "DELETE":
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        subscriptions = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path=r'(?P<following_id>\d+)/subscribe',
        serializer_class=FollowSerializer,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, following_id=None):
        following = get_object_or_404(User, id=following_id)
        if request.method == 'POST':
            serializer = self.get_serializer(
                data={},
                context={
                    'request': request,
                    'following_id': following_id
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(
                user=self.request.user,
                following=following
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            follow = get_object_or_404(
                Follow,
                user=request.user,
                following=following
            )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
