from rest_framework import serializers
from django.core.validators import EmailValidator
from django.utils.html import escape
from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обращений клиентов с защитой от XSS
    """

    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            "required": "Имя обязательно для заполнения",
            "max_length": "Имя не должно превышать 100 символов",
        },
    )
    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator(message="Введите корректный email адрес")],
    )
    message = serializers.CharField(
        required=True,
        max_length=5000,
        error_messages={
            "required": "Сообщение обязательно для заполнения",
            "max_length": "Сообщение не должно превышать 5000 символов",
        },
    )

    class Meta:
        model = Contact
        fields = ["id", "name", "email", "message"]

    def validate_name(self, value):
        """Защита от XSS в имени"""
        return escape(value.strip())

    def validate_message(self, value):
        """Защита от XSS в сообщении"""
        cleaned = escape(value.strip())
        if len(cleaned) < 10:
            raise serializers.ValidationError(
                "Сообщение должно содержать минимум 10 символов"
            )
        return cleaned
