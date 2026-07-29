"""Учебный шаблон для настроек проекта RAG бота."""

from __future__ import annotations

from pathlib import Path
from typing import Set

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


CURRENT_FILE_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_FILE_DIR.parent.parent / ".env"

class Settings(BaseSettings):

    # === Telegram ===
    telegram_bot_token: str = Field(
        ...,  # обязательное поле (no default)
        description="Токен бота Telegram, получаемый у @BotFather",
        alias="TELEGRAM_BOT_TOKEN",  # явно указываем имя переменной
    )

    allowed_user_ids: Set[int] = Field(
        default=set(),
        description="Множество ID пользователей, которым разрешён доступ (через запятую)",
        alias="TG_ALLOWED_USER_IDS",
    )

    # === GigaChat ===
    gigachat_credentials: str = Field(
        ...,
        description="Учетные данные для доступа к GigaChat (обычно base64-строка)",
        alias="GIGACHAT_CREDENTIALS",
    )

    gigachat_scope: str = Field(
        default="GIGACHAT_API_PERS",
        description="Скоуп доступа GigaChat",
        alias="GIGACHAT_SCOPE",
    )

    gigachat_model: str = Field(
        default="GigaChat-2",
        description="Имя модели GigaChat",
        alias="GIGACHAT_MODEL",
    )

    gigachat_verify_ssl: bool = Field(
        default=False,
        description="Проверять SSL-сертификаты при запросах к GigaChat",
        alias="GIGACHAT_VERIFY_SSL",
    )

    # === HuggingFace ===
    hf_token: str = Field(
        default="",
        description="Токен hf",
        alias="HF_TOKEN",
    )

    hf_embedding_model: str = Field(
        default="BAAI/bge-m3",
        description="Имя модели эмбеддингов на hf",
        alias="HF_EMBEDDING_MODEL",
    )

    # === RAG pipeline ===
    faq_source_url: str = Field(
        default="https://example.com/faq",
        description="URL источника FAQ (для парсинга)",
        alias="FAQ_SOURCE_URL",
    )

    faq_storage_dir: Path = Field(
        default=Path("./data"),
        description="Директория для хранения скачанных FAQ-файлов",
        alias="FAQ_STORAGE_DIR",
    )

    vector_store_path: Path = Field(
        default=Path("./storage/faiss_index"),
        description="Путь к директории с FAISS-индексом",
        alias="VECTOR_STORE_PATH",
    )

    top_k_results: int = Field(
        default=4,
        ge=1,
        le=100,
        description="Количество топ-результатов, возвращаемых поиском",
        alias="TOP_K_RESULTS",
    )

    # === Логирование ===
    log_level: str = Field(
        default="INFO",
        description="Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        alias="LOG_LEVEL",
    )

    # ---------- Настройки Pydantic ----------
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,                # путь к файлу .env
        env_file_encoding="utf-8",
        extra="ignore",                 # игнорировать лишние переменные
        case_sensitive=False,           # имена полей регистронезависимы
        populate_by_name=True,          # можно обращаться по имени поля или алиасу
    )

    # ---------- Валидаторы ----------
    @field_validator("allowed_user_ids", mode="before")
    @classmethod
    def parse_comma_separated_set(cls, value: str | None) -> Set[int]:
        """
        Преобразует строку вида '123, 456, 789' в множество целых чисел.
        Если передано None или пустая строка — возвращает пустое множество.
        """
        if not value:
            return set()
        result = set()
        for part in str(value).split(","):
            part = part.strip()
            if part:
                result.add(int(part))
        return result

    @field_validator("gigachat_verify_ssl", mode="before")
    @classmethod
    def parse_boolean(cls, value: str | int | bool) -> bool:
        """
        Преобразует строковые/числовые значения в булево.
        Поддерживает: 1/0, true/false, yes/no, on/off (регистронезависимо).
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            return normalized in ("1", "true", "yes", "on")
        return False


settings = Settings()
