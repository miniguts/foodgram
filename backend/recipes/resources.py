from import_export import resources

from .models import Ingredient, Tag


class TagResource(resources.ModelResource):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        export_order = ('id', 'name', 'slug')


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        export_order = ('id', 'name', 'measurement_unit')
