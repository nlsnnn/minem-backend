from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Optional

from .schemas import CalculateCostResult


class DeliveryProviderBase(ABC):

    @abstractmethod
    def calculate_delivery_cost(
        self,
        items_data: List[Dict],
        destination_address: str,
        tariff: str = "time_interval",
    ) -> CalculateCostResult:
        pass
