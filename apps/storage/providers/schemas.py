from dataclasses import dataclass
from typing import Optional


@dataclass
class UploadResult:
    """Результат загрузки файла в хранилище."""

    url: str
    file_key: str
    file_size: int
    content_type: str


@dataclass
class DeleteResult:
    """Результат удаления файла из хранилища."""

    success: bool
    file_key: Optional[str] = None
    error: Optional[str] = None
