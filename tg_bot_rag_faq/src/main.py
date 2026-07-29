"""Точка входа для учебной версии бота."""

from __future__ import annotations

import asyncio
import logging
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Меняем рабочую директорию на корень проекта
os.chdir(BASE_DIR)

from src.bot import run_bot

logging.basicConfig(level=logging.INFO)

def main() -> None:
    """Запуск бота."""
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logging.info("Bot stopped")

if __name__ == "__main__":
    main()