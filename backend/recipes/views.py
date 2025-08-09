import hashlib

from core.filters import RecipeFilter
from core.permissions import IsAuthorOrReadOnly
from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ShortRecipeSerializer,
                          TagSerializer)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name']
    pagination_class = None


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipeFilter
    search_fields = ['name', 'author__id']
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    ]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'tags', 'ingredient_links__ingredient'
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def short_link(self, request, pk=None):
        recipe = self.get_object()
        hash_val = hashlib.md5(
            f"{settings.SECRET_KEY}{recipe.id}".encode()
        ).hexdigest()[:8]
        short_url = request.build_absolute_uri(f"/r/{hash_val}/")
        return Response({'short-link': short_url})


class AddRemoveRecipeBaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    model = None

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj, created = self.model.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if not created:
            return Response({'errors': 'Уже добавлено'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(ShortRecipeSerializer(recipe).data,
                        status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        deleted, _ = self.model.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted:
            return Response({'errors': 'Не найдено'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(AddRemoveRecipeBaseView):
    model = Favorite


class ShoppingCartView(AddRemoveRecipeBaseView):
    model = ShoppingCart


class DownloadCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        recipes_in_cart = ShoppingCart.objects.filter(
            user=request.user).values_list('recipe', flat=True)

        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__in=recipes_in_cart)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total=Sum('amount'))
            .order_by('ingredient__name')
        )

        lines = [
            f"{item['ingredient__name']}"
            f" ({item['ingredient__measurement_unit']}) — {item['total']}"
            for item in ingredients
        ]
        content = '\n'.join(lines)

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           ' filename="shopping_cart.txt"')
        return response
