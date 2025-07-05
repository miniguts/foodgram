from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    FavoriteView,
    ShoppingCartView,
    DownloadCartView,
)
from .views import (
    SubscribeView,
    SubscriptionsListView,
    CustomUserViewSet,
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'users/<int:id>/subscribe/',
        SubscribeView.as_view(), name='subscribe'
    ),
    path(
        'users/subscriptions/',
        SubscriptionsListView.as_view(), name='subscriptions'
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteView.as_view(), name='favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartView.as_view(), name='shopping_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadCartView.as_view(), name='download_shopping_cart'
    ),
    path('', include(router.urls)),
]
