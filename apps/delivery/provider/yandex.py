import logging
import requests
from decimal import Decimal
from typing import Dict, List, Optional

from django.conf import settings

from .base import DeliveryProviderBase
from .schemas import CalculateCostResult

logger = logging.getLogger(__name__)


class YandexDeliveryProvider(DeliveryProviderBase):

    def __init__(self):
        self.base_url = settings.YANDEX_DELIVERY_BASE_URL
        self.api_key = settings.YANDEX_DELIVERY_API_KEY
        self.warehouse_id = settings.YANDEX_DELIVERY_WAREHOUSE_ID

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _calculate_total_weight(self, items_data: List[Dict]) -> int:
        total_weight = 0
        for item in items_data:
            variant = item["product_variant"]
            quantity = item.get("quantity", 1)
            weight = getattr(variant, "weight", 500)
            total_weight += weight * quantity
        return total_weight

    def _calculate_assessed_price(self, items_data: List[Dict]) -> int:
        total = Decimal("0")
        for item in items_data:
            price = Decimal(str(item.get("price", 0)))
            quantity = item.get("quantity", 1)
            total += price * quantity
        return int(total * 100)

    def _build_places(self, items_data: List[Dict]) -> List[Dict]:
        places = []
        for item in items_data:
            variant = item["product_variant"]
            quantity = item.get("quantity", 1)

            dx = getattr(variant, "dimension_length", 30)
            dy = getattr(variant, "dimension_height", 10)
            dz = getattr(variant, "dimension_width", 20)
            weight = getattr(variant, "weight", 500)

            places.append(
                {
                    "physical_dims": {
                        "weight_gross": weight * quantity,
                        "dx": dx,
                        "dy": dy,
                        "dz": dz,
                    }
                }
            )

        return places

    def calculate_delivery_cost(
        self,
        items_data: List[Dict],
        destination_address: str,
        tariff: str = "time_interval",
    ) -> CalculateCostResult:
        url = f"{self.base_url}/pricing-calculator"

        total_weight = self._calculate_total_weight(items_data)
        assessed_price = self._calculate_assessed_price(items_data)
        places = self._build_places(items_data)

        payload = {
            "source": {"platform_station_id": self.warehouse_id},
            "destination": {"address": destination_address},
            "tariff": tariff,
            "total_weight": total_weight,
            "total_assessed_price": assessed_price,
            "client_price": 0,
            "payment_method": "already_paid",
            "places": places,
        }

        try:
            response = requests.post(
                url, headers=self._get_headers(), json=payload, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            pricing_str = data.get("pricing_total", "0 RUB")
            pricing_value = (
                Decimal(pricing_str.split()[0]) if pricing_str else Decimal("0")
            )

            logger.info(f"Delivery cost calculated: {pricing_value} RUB")

            return CalculateCostResult(
                cost=pricing_value,
                delivery_days=data.get("delivery_days", 0),
                raw_response=data,
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Yandex Delivery API error (pricing-calculator): {e}")
            print(e.response.text if hasattr(e, "response") else str(e))
            print(e.response.json() if hasattr(e, "response") else str(e))
            raise Exception(f"Ошибка при расчете стоимости доставки: {e}")
