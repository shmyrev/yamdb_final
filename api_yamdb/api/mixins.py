from rest_framework.generics import DestroyAPIView, ListCreateAPIView 
from rest_framework.viewsets import GenericViewSet
from rest_framework import filters, status
from rest_framework.response import Response

from .permissions import IsAdmin


class MixinViewSet(ListCreateAPIView,
                   DestroyAPIView,
                   GenericViewSet):
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
