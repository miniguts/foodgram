from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import LimitPageNumberPagination
from users.models import Subscription
from .serializers import (
    SubscriptionSerializer, UserSerializer,
    SetPasswordSerializer, UserCreateSerializer,
    AvatarSerializer
)

User = get_user_model()


class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription, created = Subscription.objects.get_or_create(
            user=user, author=author
        )
        if not created:
            return Response(
                {'errors': 'Уже подписаны'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubscriptionSerializer(
            author,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        subscription = Subscription.objects.filter(user=user, author=author)
        if not subscription.exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsListView(GenericAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitPageNumberPagination

    def get(self, request):
        authors = User.objects.filter(
            id__in=Subscription.objects.filter(
                user=request.user).values_list('author_id', flat=True)
        )

        page = self.paginate_queryset(authors)
        serializer = self.get_serializer(
            page if page is not None else authors,
            many=True,
            context=self.get_serializer_context()
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomUserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        methods=['put', 'delete'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            avatar_url = (
                request.build_absolute_uri(user.avatar.url)
                if user.avatar else None
            )
            return Response({'avatar': avatar_url}, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            user.avatar.delete(save=True)
            return (
                Response({'status': 'Аватар удалён'},
                         status=status.HTTP_204_NO_CONTENT)
            )

    @action(
        methods=['post'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path='set_password',
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(current_password):
            return Response(
                {'current_password': 'Неверный текущий пароль'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return (
            Response({'status': 'Пароль обновлён'},
                     status=status.HTTP_204_NO_CONTENT)
        )
