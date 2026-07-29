"""Асинхронный слой для работы с SQLite (хранение истории чатов)."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

import aiosqlite

logger = logging.getLogger(__name__)

# Путь к файлу БД (можно настроить через Settings)
DB_PATH = Path(__file__).parent.parent / "storage" / "chat.db"


async def init_db() -> None:
    """Создаёт таблицу chat_history, если она не существует."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Индекс для быстрой выборки по user_id и timestamp
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_timestamp "
            "ON chat_history (user_id, timestamp DESC)"
        )
        await db.commit()
    logger.info("База данных инициализирована: %s", DB_PATH)


async def save_message(user_id: int, role: str, message: str) -> None:
    """Сохраняет одно сообщение в историю."""
    if not message:
        return
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            await db.execute(
                "INSERT INTO chat_history (user_id, role, message) VALUES (?, ?, ?)",
                (user_id, role, message.strip()),
            )
            await db.commit()
    except (sqlite3.Error, aiosqlite.Error) as e:
        logger.error("Ошибка сохранения сообщения (user=%s, role=%s): %s", user_id, role, e)
        # Не перевыбрасываем, чтобы бот не упал


async def get_recent_messages(user_id: int, limit: int = 10) -> List[Tuple[str, str]]:
    """
    Возвращает последние limit сообщений для пользователя в формате
    [(role, message), ...] в хронологическом порядке (от старого к новому).
    """
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            async with db.execute(
                """
                SELECT role, message FROM chat_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (user_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                # Переворачиваем, чтобы получить порядок от старого к новому
                return list(reversed(rows))
    except (sqlite3.Error, aiosqlite.Error) as e:
        logger.error("Ошибка получения истории (user=%s): %s", user_id, e)
        return []


async def cleanup_old_messages(days: int = 7) -> int:
    """Удаляет сообщения старше указанного числа дней. Возвращает количество удалённых."""
    cutoff = datetime.now() - timedelta(days=days)
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            cursor = await db.execute(
                "DELETE FROM chat_history WHERE timestamp < ?",
                (cutoff.isoformat(),),
            )
            await db.commit()
            deleted = cursor.rowcount
            logger.info("Удалено %d старых сообщений (старше %d дней)", deleted, days)
            return deleted
    except (sqlite3.Error, aiosqlite.Error) as e:
        logger.error("Ошибка очистки старых записей: %s", e)
        return 0