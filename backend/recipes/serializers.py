from rest_framework import serializers

from api.serializers import UserSerializer
from core.fields import Base64ImageField

from .models import Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = IngredientInRecipe
        fields = ["id", "name", "measurement_unit", "amount"]


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        source="ingredient_links", many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return obj.shopping_carts.filter(user=user).exists()


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ["id", "name", "text", "image",
                  "cooking_time", "ingredients", "tags"]

    def validate(self, attrs):
        ingredients = attrs.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Нужно указать хотя бы один ингредиент."}
            )

        ingredient_ids = []
        for item in ingredients:
            ingredient_id = item["id"].id
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    {"ingredients": "Ингредиенты не должны повторяться."}
                )
            ingredient_ids.append(ingredient_id)

            if item["amount"] < 1:
                raise serializers.ValidationError(
                    {
                        "ingredients": (
                            "Количество каждого ингредиента"
                            " должно быть больше 0."
                        )
                    }
                )

        tags = attrs.get("tags")
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Нужно указать хотя бы один тег."}
            )

        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                {"tags": "Теги не должны повторяться."})

        cooking_time = attrs.get("cooking_time")
        if cooking_time < 1:
            raise serializers.ValidationError(
                {"cooking_time": "Время приготовления должно быть больше 0."}
            )

        return attrs

    def create_ingredients(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=item["id"],
                    amount=item["amount"],
                )
                for item in ingredients
            ]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.tags.set(tags)
        instance.ingredient_links.all().delete()
        self.create_ingredients(ingredients, instance)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
