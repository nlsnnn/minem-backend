import logging
import mimetypes
from pathlib import Path
from typing import Optional

from django.core.files.uploadedfile import UploadedFile

from .providers import YandexStorageProvider
from .providers.base import StorageProviderBase
from .providers.schemas import DeleteResult, UploadResult

logger = logging.getLogger(__name__)


class StorageService:
    """Сервис для управления загрузкой и удалением файлов."""

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(self, storage_provider: Optional[StorageProviderBase] = None):
        """
        Инициализация сервиса хранилища.

        Args:
            storage_provider: Провайдер хранилища (по умолчанию YandexStorageProvider)
        """
        self.storage_provider = storage_provider or YandexStorageProvider()

    def upload(
        self,
        file: UploadedFile,
        path_prefix: str = "products",
        validate: bool = True,
    ) -> UploadResult:
        """
        Загрузка файла в хранилище.

        Args:
            file: Загружаемый файл
            path_prefix: Префикс пути для организации файлов
            validate: Проводить ли валидацию файла

        Returns:
            UploadResult с публичным URL и метаданными файла

        Raises:
            ValueError: Если файл не прошёл валидацию
            Exception: Если произошла ошибка при загрузке
        """
        try:
            if validate:
                self._validate_file(file)

            content_type = self._get_content_type(file.name)

            logger.info(
                f"Начало загрузки файла: {file.name} ({file.size} байт), тип: {content_type}"
            )

            result = self.storage_provider.upload_file(
                file=file.file,
                filename=file.name,
                content_type=content_type,
                path_prefix=path_prefix,
            )

            logger.info(f"Файл успешно загружен: {result.url}")
            return result

        except ValueError as e:
            logger.error(f"Ошибка валидации файла {file.name}: {str(e)}")
            raise
        except Exception as e:
            logger.error(
                f"Ошибка при загрузке файла {file.name}: {str(e)}", exc_info=True
            )
            raise

    def delete(self, file_url: str) -> DeleteResult:
        """
        Удаление файла из хранилища.

        Args:
            file_url: Публичный URL файла для удаления

        Returns:
            DeleteResult с результатом операции
        """
        try:
            logger.info(f"Начало удаления файла: {file_url}")

            result = self.storage_provider.delete_file(file_url)

            if result.success:
                logger.info(f"Файл успешно удалён: {file_url}")
            else:
                logger.error(
                    f"Не удалось удалить файл: {file_url}, ошибка: {result.error}"
                )

            return result

        except Exception as e:
            logger.error(
                f"Ошибка при удалении файла {file_url}: {str(e)}", exc_info=True
            )
            return DeleteResult(success=False, error=str(e))

    def cleanup_unused(
        self, file_url: str, model_class, field_name: str = "url"
    ) -> bool:
        """
        Удаление файла, если он больше не используется в указанной модели.

        Args:
            file_url: URL файла для проверки и удаления
            model_class: Класс модели для проверки использования
            field_name: Имя поля с URL (по умолчанию "url")

        Returns:
            True если файл был удалён, False если он всё ещё используется или не удалён
        """
        try:
            # Проверяем, используется ли файл в других записях
            filter_kwargs = {field_name: file_url}
            usage_count = model_class.objects.filter(**filter_kwargs).count()

            if usage_count > 1:
                logger.info(
                    f"Файл {file_url} используется в {usage_count} записях, пропускаем удаление"
                )
                return False

            if usage_count == 0:
                logger.warning(
                    f"Файл {file_url} не найден в базе данных, но будет удалён из хранилища"
                )

            result = self.delete(file_url)
            return result.success

        except Exception as e:
            logger.error(
                f"Ошибка при очистке неиспользуемого файла {file_url}: {str(e)}",
                exc_info=True,
            )
            return False

    def _validate_file(self, file: UploadedFile) -> None:
        """
        Валидация загружаемого файла.

        Args:
            file: Загружаемый файл

        Raises:
            ValueError: Если файл не прошёл валидацию
        """
        if not file:
            raise ValueError("Файл не предоставлен")

        if file.size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"Размер файла превышает максимально допустимый: "
                f"{file.size} > {self.MAX_FILE_SIZE} байт"
            )

        extension = Path(file.name).suffix.lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Недопустимое расширение файла: {extension}. "
                f"Разрешены: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

    def _get_content_type(self, filename: str) -> str:
        """
        Определение MIME-типа файла по расширению.

        Args:
            filename: Имя файла

        Returns:
            MIME-тип файла
        """
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"
