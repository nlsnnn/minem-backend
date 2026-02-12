import logging
from decimal import Decimal
from typing import Dict, List

from django.conf import settings

from .provider import YandexDeliveryProvider

logger = logging.getLogger(__name__)


class DeliveryService:
    """
    Сервис для расчета стоимости доставки.
    Использует API Яндекс Доставки с fallback на фиксированную стоимость.
    """

    def __init__(self):
        self.provider = YandexDeliveryProvider()
        self.default_cost = Decimal(settings.DEFAULT_DELIVERY_COST)

    def calculate_delivery_cost(
        self,
        items_data: List[Dict],
        destination_address: str,
        tariff: str = "time_interval",
    ) -> Decimal:
        """
        Рассчитывает стоимость доставки.
        При ошибке API возвращает DEFAULT_DELIVERY_COST.
        
        Args:
            items_data: Список товаров с их параметрами
            destination_address: Адрес доставки
            tariff: Тариф ('time_interval' или 'self_pickup')
        
        Returns:
            Decimal: Стоимость доставки
        """
        try:
            result = self.provider.calculate_delivery_cost(
                items_data=items_data,
                destination_address=destination_address,
                tariff=tariff,
            )
            logger.info(
                f"Yandex delivery cost calculated: {result.cost} RUB"
            )
            return result.cost
            
        except Exception as e:
            logger.warning(
                f"Failed to calculate delivery via Yandex API: {e}. "
                f"Using default cost: {self.default_cost} RUB"
            )
            return self.default_cost
