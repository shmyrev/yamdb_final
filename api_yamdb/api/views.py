from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User
from reviews.models import Title, Category, Genre, Review
from .filters import TitleFilter
from .permissions import (IsAdmin,
                          IsAdminOrIsModeratorOrIsUser,
                          IsAdminOrReadOnly)

from .serializers import (AdminSerializer,
                          JWTTokenSerializer,
                          UserSerializer,
                          CategorySerializer,
                          GenreSerializer,
                          TitleCreateSerializer,
                          TitleReadSerializer,
                          CommentSerializer,
                          ReviewSerializer)
from .utils import send_confirmation_code_on_email
from .mixins import MixinViewSet


class SignUp(APIView):
    """Вьюкласс для регистрации пользователей"""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        user = User.objects.filter(
            username=request.data.get("username"),
            email=request.data.get("email")
        ).first()

        if user:
            send_confirmation_code_on_email(user.username, user.email)

            return Response(status=status.HTTP_200_OK)

        if serializer.is_valid():
            try:
                User.objects.get_or_create(
                    username=serializer.data.get('username'),
                    email=serializer.data.get('email'))
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            send_confirmation_code_on_email(
                serializer.data['username'], serializer.data['email'])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIToken(APIView):
    """Вьюкласс для получения токена"""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = JWTTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = get_object_or_404(
                User, username=serializer.data['username'])
            if default_token_generator.check_token(
               user, serializer.data['confirmation_code']):
                token = AccessToken.for_user(user)

                return Response(
                    {'token': str(token)}, status=status.HTTP_200_OK)

            return Response(
                {'confirmation_code': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы админа с пользователями"""

    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'delete', 'patch', ]

    @action(detail=False, methods=('get', 'patch'),
            url_name='me', permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = AdminSerializer(
            request.user,
            data=request.data,
            partial=True)
        if serializer.is_valid():
            serializer.save(role=self.request.user.role)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(MixinViewSet):
    """CategoryViewSet категории произведений."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(MixinViewSet):
    """GenreViewSet жанры произведений."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    """TitleViewSet произведения, к которым пишут отзывы."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ReviewViewSet отзывы на произведения."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrIsModeratorOrIsUser,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """CommentViewSet комментарии к отзывам."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrIsModeratorOrIsUser,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, pk=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
