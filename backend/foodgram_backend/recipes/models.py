from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import shortuuid

from users.constants import INGREDIENT_AMOUNT_MIN


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Название',
        help_text='Введите название тега'
    )
    slug = models.SlugField(
        unique=True,
        max_length=32,
        verbose_name='URL-адерс',
        help_text='Введите URL-адрес'
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        """
        Метаданные модели Tag.

        Атрибуты:
            - verbose_name: Название модели в единственном числе.
            - verbose_name_plural: Название модели во множественном числе.
        """

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredients(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения'
    )

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'

    class Meta:
        """
        Метаданные модели Ingredients.

        Атрибуты:
            - verbose_name: Название модели в единственном числе.
            - verbose_name_plural: Название модели во множественном числе.
        """

        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='Укажите автора',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        verbose_name='Изображение',
        help_text='Добавитье изображение к рецепту'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингридиенты',
        help_text='Выберите ингридиенты для рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Выберите теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        verbose_name='Время готовки',
        help_text='Укажите время готовки в минутах от 1 минуты до 24ч',
    )
    short_id = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Сокращенная ссылка',
        help_text='Сокращенная ссылка на рецепт'
    )

    def __str__(self):
        return f'{self.author.username} - {self.name}'

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = shortuuid.ShortUUID().random(length=6)
        super().save(*args, **kwargs)

    def get_short_url(self, request=None):
        if request:
            return request.build_absolute_uri(f'/r/{self.short_id}/')
        return f'/r/{self.short_id}/'

    class Meta:
        """
        Метаданные модели Ingredients.

        Атрибуты:
            - verbose_name: Название модели в единственном числе.
            - verbose_name_plural: Название модели во множественном числе.
        """

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        help_text='Укажите рецепт',
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        help_text='Укажите ингредиент',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            INGREDIENT_AMOUNT_MIN,
            f'Минимальное количество {INGREDIENT_AMOUNT_MIN}'
        ),),
        help_text='Укажите количество',
        verbose_name='Количество'
    )

    def __str__(self):
        return (f'{self.recipe.name} - {self.ingredient.name} -'
                f'{self.amount} {self.ingredient.measurement_unit}')

    class Meta:
        """
        Метаданные модели IngrediRecipeIngredientents.

        Атрибуты:
            - verbose_name: Название модели в единственном числе.
            - verbose_name_plural: Название модели во множественном числе.
        """

        verbose_name = 'Ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        unique=True,
        help_text='Пользователь устанавливается автоматически',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        help_text='Укажите рецепт, чтобы добавить в избранное',
        verbose_name='Избранное',
        unique=True,
    )

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'

    class Meta:
        """
        Метаданные модели Favorite.

        Атрибуты:
            - verbose_name: Название модели в единственном числе.
            - verbose_name_plural: Название модели во множественном числе.
        """

        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopper',
        verbose_name='Покупатель',
        help_text='Укажите покупателя',
    )
    recipe = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
        help_text='Выберите рецепты для покупки ингридиентов',
        related_name='in_shopping_lists'
    )

    def __str__(self):
        """Возвращает строковое представление списка покупок."""
        return f'{self.user.username} '

    class Meta:
        """Метаданные модели ShoppingList."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        unique_together = ('user',)


class ShoppingListItem(models.Model):
    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        verbose_name='Список покупок',
        help_text='Укажите список покупок'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
        help_text='Укажите Ингредиенты'
    )
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='Количество',
        help_text='Укажите количество'
    )

    class Meta:
        """
        Метаданные модели ShoppingListItem.

        Атрибуты:
            - verbose_name: Название модели в единственном числе.
            - verbose_name_plural: Название модели во множественном числе.
        """

        verbose_name = 'Ингридиент в списке покупок'
        verbose_name_plural = 'Ингридиенты в списках покупок'
