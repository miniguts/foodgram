import django_filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(field_name="tags__slug")
    author = django_filters.NumberFilter(field_name="author__id")
    is_favorited = django_filters.NumberFilter(method="filter_is_favorited")
    is_in_shopping_cart = django_filters.NumberFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ["tags", "author", "is_favorited", "is_in_shopping_cart"]

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if int(value) else queryset
        if int(value):
            return queryset.filter(favorites__user=user)
        return queryset.exclude(favorites__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if int(value) else queryset
        if int(value):
            return queryset.filter(shopping_carts__user=user)
        return queryset.exclude(shopping_carts__user=user)


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains")

    class Meta:
        model = Ingredient
        fields = ["name"]
