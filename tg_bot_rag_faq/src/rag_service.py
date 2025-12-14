"""Учебная версия RAG сервиса. Заполните пропуски."""

from __future__ import annotations

import logging
from functools import cached_property
from typing import Any

from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import GigaChat
from langchain_community.embeddings import GigaChatEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from .config_empty import Settings  # можно переключиться на боевой config после реализации

logger = logging.getLogger(__name__)


ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "TODO: опишите роль ассистента"),
        ("human", "TODO: передайте контекст и вопрос"),
    ]
)


class RAGService:
    """Скелет, где нужно реализовать шаги RAG."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @cached_property
    def embeddings(self) -> GigaChatEmbeddings:
        raise NotImplementedError("Создайте GigaChatEmbeddings")

    @cached_property
    def retriever(self):
        # Подсказка: загрузите локальный FAISS и верните retriever через as_retriever(k=...)
        raise NotImplementedError("Верните поисковик документов")

    @cached_property
    def llm(self) -> GigaChat:
        raise NotImplementedError("Инициализируйте GigaChat LLM")

    @cached_property
    def chain(self):
        logger.info("TODO: соберите базовую цепочку")
        answer_chain = ANSWER_PROMPT | ... | StrOutputParser()

        def _invoke(payload: dict[str, Any]):
            # 1. Достаньте вопрос из payload
            # 2. Получите документы через retriever
            # 3. Соберите строку контекста ("\n---\n".join(...))
            # 4. Вызовите answer_chain
            # 5. Верните dict с ключами answer и source_documents
            raise NotImplementedError

        return RunnableLambda(_invoke)

    def ask(self, question: str) -> dict[str, Any]:
        return self.chain.invoke({"question": question})


__all__ = ["RAGService"]
