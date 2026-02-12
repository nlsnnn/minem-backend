from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class CalculateCostResult:
    cost: Decimal
    delivery_days: int
    currency: str = "RUB"
    raw_response: Optional[dict] = None
