from rest_framework import generics, permissions


from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from apps.common.throttling import OrderCreateThrottle


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
    throttle_classes = [OrderCreateThrottle]
