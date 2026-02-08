from rest_framework import generics, permissions

from .models import Contact
from .serializers import ContactSerializer
from apps.common.throttling import ContactFormThrottle


class ContactCreateView(generics.CreateAPIView):
    """
    Представление для создания нового обращения.
    Лимит: 3 сообщения в час с одного IP.
    """

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ContactFormThrottle]
