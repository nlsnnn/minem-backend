import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from .base import StorageProviderBase
from .schemas import DeleteResult, UploadResult

logger = logging.getLogger(__name__)


class YandexStorageProvider(StorageProviderBase):
    """Провайдер для Yandex Cloud Object Storage."""

    def __init__(self):
        """Инициализация клиента S3 для Yandex Cloud."""
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.YANDEX_STORAGE_ENDPOINT,
            aws_access_key_id=settings.YANDEX_STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.YANDEX_STORAGE_SECRET_KEY,
            region_name=settings.YANDEX_STORAGE_REGION,
        )
        self.bucket_name = settings.YANDEX_STORAGE_BUCKET_NAME

    def upload_file(
        self, file: BinaryIO, filename: str, content_type: str, path_prefix: str = ""
    ) -> UploadResult:
        """
        Загрузка файла в Yandex Cloud Object Storage.

        Args:
            file: Файловый объект для загрузки
            filename: Оригинальное имя файла
            content_type: MIME-тип файла
            path_prefix: Префикс пути (по умолчанию "products")

        Returns:
            UploadResult с публичным URL и метаданными файла
        """
        try:
            file_key = self._generate_file_key(filename, path_prefix)
            file.seek(0)
            file_size = len(file.read())
            file.seek(0)

            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                file_key,
                ExtraArgs={
                    "ContentType": content_type,
                    "ACL": "public-read",
                },
            )

            public_url = self._get_public_url(file_key)

            logger.info(
                f"Файл успешно загружен: {file_key} ({file_size} байт), URL: {public_url}"
            )

            return UploadResult(
                url=public_url,
                file_key=file_key,
                file_size=file_size,
                content_type=content_type,
            )

        except ClientError as e:
            error_msg = f"Ошибка при загрузке файла в S3: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

    def delete_file(self, file_url: str) -> DeleteResult:
        """
        Удаление файла из Yandex Cloud Object Storage.

        Args:
            file_url: Публичный URL файла для удаления

        Returns:
            DeleteResult с результатом операции
        """
        try:
            file_key = self._extract_key_from_url(file_url)

            if not file_key:
                error_msg = f"Не удалось извлечь ключ файла из URL: {file_url}"
                logger.error(error_msg)
                return DeleteResult(success=False, error=error_msg)

            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)

            logger.info(f"Файл успешно удалён: {file_key}")

            return DeleteResult(success=True, file_key=file_key)

        except ClientError as e:
            error_msg = f"Ошибка при удалении файла из S3: {str(e)}"
            logger.error(error_msg)
            return DeleteResult(success=False, error=error_msg)

    def _generate_file_key(self, filename: str, path_prefix: str = "") -> str:
        """
        Генерация уникального ключа файла для хранения в S3.

        Args:
            filename: Оригинальное имя файла
            path_prefix: Префикс пути (например, "products")

        Returns:
            Уникальный ключ файла: prefix/uuid_timestamp.ext
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:12]
        extension = Path(filename).suffix.lower()

        prefix = path_prefix or "products"
        file_key = f"{prefix}/{unique_id}_{timestamp}{extension}"

        return file_key

    def _get_public_url(self, file_key: str) -> str:
        """
        Формирование публичного URL для файла в бакете.

        Args:
            file_key: Ключ файла в S3

        Returns:
            Публичный URL файла
        """
        return f"{settings.YANDEX_STORAGE_ENDPOINT}/{self.bucket_name}/{file_key}"

    def _extract_key_from_url(self, file_url: str) -> str:
        """
        Извлечение ключа файла из публичного URL.

        Args:
            file_url: Публичный URL файла

        Returns:
            Ключ файла в S3
        """
        try:
            parsed_url = urlparse(file_url)
            path_parts = parsed_url.path.strip("/").split("/", 1)

            if len(path_parts) == 2 and path_parts[0] == self.bucket_name:
                return path_parts[1]

            return ""
        except Exception as e:
            logger.error(f"Ошибка при извлечении ключа из URL {file_url}: {str(e)}")
            return ""
