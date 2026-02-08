from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle


class OrderCreateThrottle(AnonRateThrottle):
    """
    Лимит на создание заказов: 5 заказов в минуту с одного IP.
    Защита от спама и блокировки всех товаров.
    """

    rate = "5/minute"
    scope = "order_create"


class ContactFormThrottle(AnonRateThrottle):
    """
    Лимит на форму обратной связи: 3 сообщения в час с одного IP.
    """

    rate = "3/hour"
    scope = "contact_form"


class WebhookThrottle(SimpleRateThrottle):
    """
    Лимит на вебхуки: 100 запросов в минуту.
    Защита от флуда вебхуков.
    """

    rate = "100/minute"
    scope = "webhook"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }
