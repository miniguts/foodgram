import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Импортирует ингредиенты и теги из JSON-файлов'

    def handle(self, *args, **kwargs):
        with open('data/ingredients.json', encoding='utf-8') as f:
            ingredients = json.load(f)
            for item in ingredients:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )

        with open('data/tags.json', encoding='utf-8') as f:
            tags = json.load(f)
            for tag in tags:
                Tag.objects.get_or_create(
                    name=tag['name'],
                    slug=tag['slug']
                )

        self.stdout.write(self.style.SUCCESS('✅ Данные успешно загружены.'))
