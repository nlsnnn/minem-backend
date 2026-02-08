from django.db import models


class Contact(models.Model):
    CONTACT_STATUS_CHOICES = [
        ("new", "Новое"),
        ("handled", "Обработан"),
    ]

    name = models.CharField(
        max_length=100, verbose_name="Имя", help_text="Имя отправителя"
    )
    email = models.EmailField(verbose_name="Email", help_text="Для ответа")
    message = models.TextField(verbose_name="Суть обращения")
    status = models.CharField(
        verbose_name="Статус обращения",
        choices=CONTACT_STATUS_CHOICES,
        default="new",
    )

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"
