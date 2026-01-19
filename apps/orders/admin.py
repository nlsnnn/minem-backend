from django.contrib import admin

from .models import Order, OrderItem, OrderCustomer

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderCustomer)
