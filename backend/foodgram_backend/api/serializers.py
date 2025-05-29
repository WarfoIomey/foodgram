import base64
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from recipes.models import Tag, Recipe, Ingredients, Favorite, ShoppingList
from users.models import Follow


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class BaseRecipeRelationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        abstract = True
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'slug'
        )


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = (
            'id', 'name', 'measurement_unit'
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    ingredients = IngredientsSerializer(read_only=True, many=True)
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'descriptions',
            'ingredients',
            'tags',
            'cooking_time'
        )


class FavoriteSerializer(BaseRecipeRelationSerializer):

    class Meta(BaseRecipeRelationSerializer.Meta):
        model = Favorite

    def validate(self, data):
        """Проверка на дубликат."""
        request = self.context.get('request')
        if Favorite.objects.filter(
            user=request.user,
            recipe=self.context.get('recipe')
        ).exists():
            raise serializers.ValidationError(
                "Рецепт уже в избранном"
            )
        return data


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field='username'
    )
    following = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def create(self, validated_data):
        user = self.context['request'].user
        following_id = self.context.get('following_id')
        following = get_object_or_404(User, id=following_id)
        if user == following:
            raise serializers.ValidationError(
                {"error": "Подписка самого на себя запрещена."}
            )
        if Follow.objects.filter(
            user=user,
            following=following
        ).exists():
            raise serializers.ValidationError(
                {"error": "Вы уже подписаны на этого автора."}
            )
        return Follow.objects.create(
            user=self.context['request'].user,
            following=following
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'avatar',
            'is_subscribed'
        )

    def create(self, validate_data):
        password = validate_data.pop('password')
        user = User(**validate_data)
        user.set_password(password)
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user,
                following=obj
            ).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления автара."""
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ('avatar',)


class ShortLinkSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'short_url']

    def get_short_url(self, obj):
        request = self.context.get('request')
        return obj.get_short_url(request)


class ShoppingCartSerializer(BaseRecipeRelationSerializer):

    class Meta(BaseRecipeRelationSerializer.Meta):
        model = ShoppingList
