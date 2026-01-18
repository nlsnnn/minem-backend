from django.contrib import admin

from .models import Payment, PaymentEvent

admin.site.register(Payment)
admin.site.register(PaymentEvent)