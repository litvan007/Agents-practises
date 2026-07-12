"""Шаблон Telegram-бота для обучения."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Dict, List, Tuple
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from .config import Settings
from .rag_service import RAGService

logger = logging.getLogger(__name__)


class TelegramRAGBot:
    """Минимальный набор методов, которые должен реализовать студент."""

    def __init__(self, settings: Settings, rag_service: RAGService) -> None:
        self.settings = settings
        self.rag_service = rag_service
        self.bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        self.dispatcher = Dispatcher()
        self.chat_history: Dict[int, List[Tuple[str, str]]] = defaultdict(list)

        self.dispatcher.message.register(self.handle_start, CommandStart())

        # TODO: добавьте остальные хендлеры (/help, обычный текст)
        self.dispatcher.message.register(self.handle_help, Command("help"))
        self.dispatcher.message.register(self.handle_message, F.text)


    async def handle_start(self, message: Message) -> None:
        user_id = message.from_user.id

        if user_id not in self.settings.allowed_user_ids:
            await message.answer(
                "Ошибка доступа!"
            )
            return

        await message.answer("""Это бот ретривер misiseek.\n
        Доступные команды:\n
        /start — начать работу\n
        /help — показать помощь""")

    async def handle_help(self, message: Message) -> None:
        """Обработчик команды /help"""
        user_id = message.from_user.id

        if user_id not in self.settings.allowed_user_ids:
            await message.answer("Ошибка доступа!")
            return

        await message.answer(
            "Задайте мне любой вопрос, и я найду ответ в базе знаний."
        )
    async def handle_message(self, message: Message) -> None:
        """Подсказка: проверьте доступ, вызовите RAG и верните ответ + источники."""

        user_id = message.from_user.id

        if user_id not in self.settings.allowed_user_ids:
            await message.answer(
                "Ошибка доступа!"
            )
            return
        question = message.text
        result= await self.rag_service.ask(question)
        answer=result["answer"]
        source_documents = result.get("source_documents", [])
        self.chat_history[user_id].append(
            (question, answer)
        )

        response = answer

        if source_documents:
            response += "\n\nИсточники:\n"

            for i, doc in enumerate(source_documents, start=1):
                source = doc.metadata.get("source", "Неизвестный источник")
                response += f"{i}. {source}\n"

        await message.answer(response)

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
