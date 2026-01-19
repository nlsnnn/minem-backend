import uuid
from yookassa import Configuration, Payment
from django.conf import settings

from .base import PaymentProviderBase
from .schemas import CreatePaymentResult


Configuration.configure(
    account_id=settings.YOOKASSA_ACCOUNT_ID,
    secret_key=settings.YOOKASSA_SECRET_KEY,
)


class YookassaProvider(PaymentProviderBase):
    """Провайдер платежей YooKassa."""

    def get_payment(self, payment_id: str):
        """Получение информации о платеже по его ID."""
        payment = Payment.find_one(payment_id)
        return payment

    def create_payment(
        self,
        order_id: str,
        amount: float,
        currency: str = "RUB",
        return_url: str = None,
        payment_method: str = "bank_card",
        customer_email: str = None,
    ) -> CreatePaymentResult:
        """Создание платежа через YooKassa."""

        idempotence_key = str(uuid.uuid4())
        payment = Payment.create(
            {
                "amount": {
                    "value": str(amount),
                    "currency": currency,
                },
                "payment_method_data": {"type": payment_method},
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url
                    if return_url
                    else self._get_return_url(order_id),
                },
                "capture": True,
                "description": f"Заказ №{order_id}",
                # "statements": {
                #     "type": "payment_overview",
                #     "delivery_method": {
                #         "type": "email",
                #         "address": customer_email,
                #     },
                # },
            },
            idempotence_key,
        )

        return CreatePaymentResult(
            confirmation_url=payment.confirmation.confirmation_url,
            payment_id=payment.id,
            status=payment.status,
            payment=payment,
        )

    def _get_return_url(self, order_id: str) -> str:
        return settings.FRONTEND_URL + "/order/info?id=" + str(order_id)
