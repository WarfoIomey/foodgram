# Generated by Django 3.2.3 on 2025-06-02 03:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_auto_20250531_1433'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shoppinglist',
            old_name='recipes',
            new_name='recipe',
        ),
    ]
