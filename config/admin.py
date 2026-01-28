from django.contrib import admin
from django.utils.html import format_html


class CustomAdminSite(admin.AdminSite):
    site_header = "Управление интернет-магазином"
    site_title = "Админ-панель"
    index_title = "Добро пожаловать в панель управления магазином"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        extra_context["instructions"] = format_html(
            """
            <div style="background: #e8f4f8; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 4px solid #2196F3;">
                <h2 style="margin-top: 0; color: #1976D2;">Быстрый старт</h2>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #1976D2; margin-bottom: 10px;">Как добавить новый товар:</h3>
                    <ol style="line-height: 1.8; color: #555;">
                        <li><strong>Подготовка:</strong> Убедитесь что созданы нужные <a href="/admin/main/size/">размеры</a> и <a href="/admin/main/color/">цвета</a></li>
                        <li><strong>Создайте базовый товар:</strong> Перейдите в раздел <a href="/admin/main/productgroup/add/">«Базовые товары»</a> и укажите название, описание, состав</li>
                        <li><strong>Добавьте цветовые варианты:</strong> В разделе <a href="/admin/main/product/">«Товары в продаже»</a> создайте товар для каждого цвета</li>
                        <li><strong>Укажите размеры и остатки:</strong> В карточке товара добавьте доступные размеры и их количество на складе</li>
                        <li><strong>Загрузите фото:</strong> Добавьте фотографии товара через инлайн "Фотографии и медиа"</li>
                        <li><strong>Опубликуйте:</strong> Поставьте галочку «Показывать на сайте» у базового товара и всех его цветов</li>
                    </ol>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #1976D2; margin-bottom: 10px;">Работа с заказами:</h3>
                    <ul style="line-height: 1.8; color: #555;">
                        <li>Новые заказы появляются в разделе <a href="/admin/orders/order/">«Заказы»</a> со статусом "Ожидает оплаты"</li>
                        <li>После оплаты статус меняется автоматически на "Оплачен"</li>
                        <li>Используйте массовые действия для изменения статусов (выделите заказы → выберите действие)</li>
                        <li>Вся история изменений остатков доступна в разделе <a href="/admin/orders/stockhistory/">«История остатков»</a></li>
                    </ul>
                </div>
                
                <div>
                    <h3 style="color: #1976D2; margin-bottom: 10px;">Полезные советы:</h3>
                    <ul style="line-height: 1.8; color: #555;">
                        <li><strong>URL товаров:</strong> Генерируется автоматически из названия (латинскими буквами)</li>
                        <li><strong>Категории:</strong> Настройте в разделе <a href="/admin/main/category/">«Категории»</a> для фильтрации в каталоге</li>
                        <li><strong>Остатки:</strong> Автоматически уменьшаются при создании заказа, следите за остатками в карточке товара</li>
                        <li><strong>Поиск:</strong> Используйте поиск по названию, артикулу или имени клиента</li>
                    </ul>
                </div>
            </div>
            """
        )

        return super().index(request, extra_context)

    def get_app_list(self, request, app_label=None):
        """
        Кастомная сортировка моделей в админке по важности
        """
        app_list = super().get_app_list(request, app_label)

        # Определяем порядок приложений
        app_order = ["orders", "main", "payment", "auth"]

        # Определяем порядок моделей для каждого приложения
        model_order = {
            "orders": ["order", "stockhistory", "orderitem", "ordercustomer"],
            "main": [
                "productgroup",
                "product",
                "productvariant",
                "category",
                "size",
                "color",
                "productmedia",
            ],
            "payment": ["payment"],  # PaymentEvent скрыт
            "auth": ["user", "group"],
        }

        # Переименовываем и группируем приложения
        app_labels = {
            "orders": "Заказы и продажи",
            "main": "Товары и каталог",
            "payment": "Платежи",
            "auth": "Пользователи и права",
        }

        # Сортируем приложения
        sorted_app_list = []
        for app_name in app_order:
            for app in app_list:
                if app["app_label"] == app_name:
                    # Переименовываем приложение
                    if app_name in app_labels:
                        app["name"] = app_labels[app_name]

                    # Сортируем модели внутри приложения
                    if app_name in model_order:
                        model_names = model_order[app_name]
                        sorted_models = []

                        for model_name in model_names:
                            for model in app["models"]:
                                if model["object_name"].lower() == model_name:
                                    sorted_models.append(model)
                                    break

                        # Добавляем модели, которых не было в списке
                        for model in app["models"]:
                            if model not in sorted_models:
                                sorted_models.append(model)

                        app["models"] = sorted_models

                    sorted_app_list.append(app)
                    break

        # Добавляем приложения, которых не было в списке
        for app in app_list:
            if app not in sorted_app_list:
                sorted_app_list.append(app)

        return sorted_app_list


# Создаем экземпляр кастомной админки
admin_site = CustomAdminSite(name="custom_admin")
