# Generated by Django 3.2.3 on 2025-05-29 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='short_id',
            field=models.CharField(blank=True, help_text='Сокращенная ссылка на рецепт', max_length=10, null=True, unique=True, verbose_name='Сокращенная ссылка'),
        ),
    ]
