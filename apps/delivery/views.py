import logging
from decimal import Decimal

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.main.models import ProductVariant
from apps.common.throttling import OrderCreateThrottle

from .serializers import DeliveryCalculateSerializer, DeliveryCalculateResponseSerializer
from .service import DeliveryService

logger = logging.getLogger(__name__)


class DeliveryCalculateView(generics.GenericAPIView):
    """
    Эндпоинт для расчета стоимости доставки без создания заказа.
    Используется в корзине для предварительного расчета.
    При ошибке API возвращает DEFAULT_DELIVERY_COST (из .env).
    
    POST /api/v1/delivery/calculate/
    
    Request:
    {
        "items": [
            {"product_variant": 14, "quantity": 1}
        ],
        "address": "Москва, Тверская улица, 1",
        "tariff": "time_interval"  # или "self_pickup"
    }
    
    Response:
    {
        "cost": "361.73",
        "delivery_days": 43,
        "currency": "RUB"
    }
    """
    serializer_class = DeliveryCalculateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [OrderCreateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        items_data = data["items"]
        address = data["address"]
        tariff = data.get("tariff", "time_interval")
        
        try:
            # Получаем варианты товаров из БД
            variant_ids = [str(item["product_variant"]) for item in items_data]
            variants = ProductVariant.objects.filter(
                id__in=variant_ids,
                is_active=True,
            ).select_related("product")
            
            if len(variants) != len(variant_ids):
                found_ids = set(str(v.id) for v in variants)
                missing_ids = set(variant_ids) - found_ids
                return Response(
                    {
                        "error": "Товары не найдены",
                        "missing_variants": list(missing_ids)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Формируем items_data для провайдера
            provider_items = []
            variants_map = {str(v.id): v for v in variants}
            
            for item in items_data:
                variant_id = str(item["product_variant"])
                variant = variants_map.get(variant_id)
                
                if variant:
                    provider_items.append({
                        "product_variant": variant,
                        "quantity": item["quantity"],
                        "price": variant.get_price(),
                    })
            
            # Рассчитываем стоимость через сервис (с fallback)
            delivery_service = DeliveryService()
            cost = delivery_service.calculate_delivery_cost(
                items_data=provider_items,
                destination_address=address,
                tariff=tariff,
            )
            
            response_serializer = DeliveryCalculateResponseSerializer({
                "cost": cost,
                "delivery_days": 0,  # Неизвестно при fallback
                "currency": "RUB",
            })
            
            return Response(response_serializer.data)
            
        except Exception as e:
            logger.error(f"Error calculating delivery cost: {e}", exc_info=True)
            return Response(
                {
                    "error": "Не удалось рассчитать стоимость доставки",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
