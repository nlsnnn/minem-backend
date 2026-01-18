from dataclasses import dataclass


@dataclass
class CreatePaymentResult:
    confirmation_url: str
    payment_id: str
    status: str
    payment: any
