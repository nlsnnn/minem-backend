from abc import ABC

from .schemas import CreatePaymentResult


class PaymentProviderBase(ABC):
    """Базовый класс для провайдеров платежей."""

    def get_payment(self, payment_id: str) -> dict:
        """
        Метод для получения платежа.
        Должен быть реализован в конкретных провайдерах.
        """
        raise NotImplementedError("Метод get_payment должен быть реализован.")

    def create_payment(
        self, amount: float, currency: str, **kwargs
    ) -> CreatePaymentResult:
        """
        Метод для создания платежного намерения.
        Должен быть реализован в конкретных провайдерах.
        """
        raise NotImplementedError("Метод create_payment должен быть реализован.")
