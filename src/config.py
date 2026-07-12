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

    if not raw:
        return set()
    result=set()

    for item in raw.split(","):
        clean_item=item.strip()
        if clean_item:
            result.add(int(clean_item))
    return result


    raise NotImplementedError("Верните множество user_id")

def _to_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")

@dataclass(slots=True)
class Settings:
    """TODO: заполните поля значениями из .env."""


    telegram_bot_token: str = field(
        default_factory=lambda: os.environ["TELEGRAM_BOT_TOKEN"]
    )

    allowed_user_ids: Set[int] = field(
        default_factory=lambda: _comma_separated_set(os.getenv("TG_ALLOWED_USER_IDS"))
    )

    gigachat_credentials: str = field(
        default_factory=lambda: os.environ["GIGACHAT_CREDENTIALS"]
    )

    gigachat_scope: str = field(
        default_factory=lambda: os.environ["GIGACHAT_SCOPE"]
    )

    gigachat_model: str = field(
        default_factory=lambda: os.environ["GIGACHAT_MODEL"]
    )

    gigachat_verify_ssl: bool = field(
        default_factory=lambda: _to_bool(os.environ["GIGACHAT_VERIFY_SSL"])
    )

    faq_source_url: str = field(
        default_factory=lambda: os.environ["FAQ_SOURCE_URL"]
    )

    faq_storage_dir: Path = field(
        default_factory=lambda: Path(os.environ["FAQ_STORAGE_DIR"])
    )

    vector_store_path: Path = field(
        default_factory=lambda: Path(os.environ["VECTOR_STORE_PATH"])
    )

    top_k_results: int = field(
        default_factory=lambda: int(os.environ["TOP_K_RESULTS"])
    )

    log_level: str = field(
        default_factory=lambda: os.environ["LOG_LEVEL"]
    )

    hf_token: str = field(
        default_factory=lambda: os.environ["HF_TOKEN"]
    )

    hf_embedding_model: str = field(
        default_factory=lambda: os.getenv(
            "HF_EMBEDDING_MODEL",
            "intfloat/multilingual-e5-base"
        )
    )
settings = Settings()
