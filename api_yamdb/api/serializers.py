from rest_framework import exceptions, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

from users.models import User, ROLES
from reviews.models import Category, Genre, Title, Review, Comment


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для пользователей"""

    email = serializers.EmailField(max_length=254,
                                   validators=[
                                       UniqueValidator(
                                           queryset=User.objects.all()),
                                   ])
    username = serializers.CharField(max_length=150,
                                     validators=[RegexValidator(
                                         regex=r'^[\w.@+-]+$',
                                         message='Недопустимый символ в имени'
                                     )])

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, username):
        username = username.lower()
        if username == "me":
            raise serializers.ValidationError(
                'Запрещенное имя для регистрации.'
            )
        return username

    def validate_email(self, email):
        if not email:
            raise serializers.ValidationError(
                'Отстутвие обязательного поля'
            )
        return email


class AdminSerializer(serializers.ModelSerializer):
    """Сериалайзер для админа"""

    email = serializers.EmailField(max_length=254,
                                   validators=[
                                       UniqueValidator(
                                           queryset=User.objects.all()
                                       )
                                   ])
    role = serializers.ChoiceField(choices=ROLES, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ("role",)


class JWTTokenSerializer(serializers.Serializer):
    """Сериалайзер для получения токена"""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(username=data['username']).exists():
            raise exceptions.NotFound(
                'Такого пользователя не существует')

        return data


class CategorySerializer(serializers.ModelSerializer):
    """CategorySerializer категории произведений."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """GenreSerializer жанры произведений."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleCreateSerializer(serializers.ModelSerializer):
    """TitleCreateSerializer произведения, к которым пишут отзывы."""
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug'
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )


class TitleReadSerializer(serializers.ModelSerializer):
    """TitleReadSerializer произведения, к которым пишут отзывы."""
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалайзер отзывы на произведения."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'title', 'author', 'pub_date', 'score')

    def validate(self, data):
        title_id = (
            self.context['request'].parser_context['kwargs']['title_id']
        )
        title = get_object_or_404(Title, pk=title_id)
        author = self.context['request'].user
        if (self.context['request'].method == 'POST'
           and Review.objects.filter(title=title, author=author).exists()):
            raise serializers.ValidationError(
                "Нельзя добавлять больше одного отзыва"
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериалайзер комментарии к отзывам."""
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'pub_date', 'text')
