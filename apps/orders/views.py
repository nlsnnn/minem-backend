from rest_framework import generics, filters, pagination, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer


class OrderDetailView(generics.RetrieveAPIView):
    """
    Представление для получения деталей заказа по его ID.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"


class OrderCreateView(generics.CreateAPIView):
    """
    Представление для создания нового заказа.
    """

    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.AllowAny]
