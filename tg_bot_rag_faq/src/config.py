"""Учебный шаблон для настроек проекта RAG бота."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set

from dotenv import load_dotenv

load_dotenv()


def _comma_separated_set(raw: str | None) -> Set[int]:
    """TODO: преобразуйте строки вида "123,456" во множество целых чисел."""
    # Подсказка: split(",") + int() внутри цикла.
    raise NotImplementedError("Верните множество user_id")


@dataclass(slots=True)
class Settings:
    """TODO: заполните поля значениями из .env."""

    telegram_bot_token: str = field(default_factory=lambda: os.environ["TELEGRAM_BOT_TOKEN"])
    allowed_user_ids: Set[int] = field(
        default_factory=lambda: _comma_separated_set(os.getenv("TG_ALLOWED_USER_IDS"))
    )
    gigachat_credentials: str = field(default_factory=lambda: ...)
    gigachat_scope: str = field(default_factory=lambda: ...)
    gigachat_model: str = field(default_factory=lambda: ...)
    gigachat_verify_ssl: bool = field(default_factory=lambda: ...)
    faq_source_url: str = field(default_factory=lambda: ...)
    faq_storage_dir: Path = field(default_factory=lambda: ...)
    vector_store_path: Path = field(default_factory=lambda: ...)
    top_k_results: int = field(default_factory=lambda: ...)
    log_level: str = field(default_factory=lambda: ...)


settings = Settings()
