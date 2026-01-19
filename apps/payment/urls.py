from django.urls import path

from . import views

urlpatterns = [
    path("webhook/", views.yookassa_webhook, name="yookassa_webhook"),
]
