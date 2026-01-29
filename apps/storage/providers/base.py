from abc import ABC
from typing import BinaryIO

from .schemas import DeleteResult, UploadResult


class StorageProviderBase(ABC):
    """Базовый класс для провайдеров файлового хранилища."""

    def upload_file(
        self, file: BinaryIO, filename: str, content_type: str, path_prefix: str = ""
    ) -> UploadResult:
        """
        Метод для загрузки файла в хранилище.
        Должен быть реализован в конкретных провайдерах.

        Args:
            file: Файловый объект для загрузки
            filename: Имя файла
            content_type: MIME-тип файла
            path_prefix: Префикс пути для организации файлов

        Returns:
            UploadResult с URL и метаданными файла
        """
        raise NotImplementedError("Метод upload_file должен быть реализован.")

    def delete_file(self, file_url: str) -> DeleteResult:
        """
        Метод для удаления файла из хранилища.
        Должен быть реализован в конкретных провайдерах.

        Args:
            file_url: URL файла для удаления

        Returns:
            DeleteResult с результатом операции
        """
        raise NotImplementedError("Метод delete_file должен быть реализован.")
