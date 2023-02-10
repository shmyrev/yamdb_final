from django.urls import include, path
from rest_framework import routers

from .views import (
    APIToken,
    SignUp,
    UserViewSet,
    TitleViewSet,
    CategoryViewSet,
    GenreViewSet,
    ReviewViewSet,
    CommentViewSet
)

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('users', UserViewSet)
router_v1.register('titles', TitleViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', SignUp.as_view(), name='signup'),
    path('v1/auth/token/', APIToken.as_view(), name='token'),
    path('v1/', include(router_v1.urls))
]
