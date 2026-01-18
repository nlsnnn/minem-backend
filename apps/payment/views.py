from rest_framework import generics, filters, pagination, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from yookassa.webhook import Webhook, WebhookRequest

from .models import Payment, PaymentEvent
from .serializers import PaymentSerializer


class PaymentDetailView(generics.RetrieveAPIView):
    """
    Представление для получения деталей платежа по его ID.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"
