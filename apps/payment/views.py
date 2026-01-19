import json
import logging

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from yookassa.domain.notification import WebhookNotification

from .service import PaymentService
from .models import Payment
from .serializers import PaymentSerializer

logger = logging.getLogger(__name__)


class PaymentDetailView(generics.RetrieveAPIView):
    """
    Представление для получения деталей платежа по его ID.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def yookassa_webhook(request):
    """
    Вебхук для обработки событий от Yookassa.
    """
    request_body = request.body

    try:
        notification = WebhookNotification(json.loads(request_body))
        logger.info(
            f"Received webhook: event={notification.event}, payment_id={notification.object.id}"
        )
    except (ValueError, json.JSONDecodeError) as e:
        logger.error(f"Invalid webhook payload: {e}")
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Webhook parsing error: {e}", exc_info=True)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        PaymentService.payment_acceptance(notification, request_body)
        logger.info(
            f"Successfully processed webhook for payment {notification.object.id}"
        )
        return Response(status=status.HTTP_200_OK)
    except Payment.DoesNotExist:
        logger.warning(f"Payment not found for webhook: {notification.object.id}")
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Payment processing error: {e}", exc_info=True)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
