# Generated by Django 3.2.3 on 2025-06-07 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_auto_20250607_1219'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ['-id'], 'verbose_name': 'Избранный рецепт', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='ingredients',
            options={'ordering': ['-id'], 'verbose_name': 'Ингридиент', 'verbose_name_plural': 'Ингридиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-id',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'ordering': ['-id'], 'verbose_name': 'Ингридиент в рецепте', 'verbose_name_plural': 'Ингридиенты в рецепте'},
        ),
        migrations.AlterModelOptions(
            name='shoppinglist',
            options={'ordering': ['-id'], 'verbose_name': 'Список покупок', 'verbose_name_plural': 'Списки покупок'},
        ),
    ]
