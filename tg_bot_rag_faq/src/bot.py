"""Шаблон Telegram-бота для обучения."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Dict, List, Tuple

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from .config_empty import Settings
from .rag_service_empty import RAGService

logger = logging.getLogger(__name__)


class TelegramRAGBot:
    """Минимальный набор методов, которые должен реализовать студент."""

    def __init__(self, settings: Settings, rag_service: RAGService) -> None:
        self.settings = settings
        self.rag_service = rag_service
        self.bot = Bot(token=settings.telegram_bot_token, parse_mode="HTML")
        self.dispatcher = Dispatcher()
        self.chat_history: Dict[int, List[Tuple[str, str]]] = defaultdict(list)

        # TODO: добавьте остальные хендлеры (/help, обычный текст)
        self.dispatcher.message.register(self.handle_start, CommandStart())

    async def handle_start(self, message: Message) -> None:
        await message.answer("TODO: представьтесь пользователю")

    async def handle_answer(self, message: Message) -> None:
        """Подсказка: проверьте доступ, вызовите RAG и верните ответ + источники."""
        raise NotImplementedError

    async def run(self) -> None:
        logger.info("Запуск учебного бота")
        await self.dispatcher.start_polling(self.bot)


async def run_bot() -> None:
    settings = Settings()
    rag = RAGService(settings)
    bot = TelegramRAGBot(settings, rag)
    await bot.run()


if __name__ == "__main__":
    asyncio.run(run_bot())
