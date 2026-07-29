"""Учебная версия RAG сервиса. Заполните пропуски."""

from __future__ import annotations

import logging
from functools import cached_property
from typing import Any
import json
from pathlib import Path
from typing import Any, List, Tuple
# Новые раздельные пакеты для aполной совместимости
from langchain_gigachat.chat_models import GigaChat
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
# Вместо: from langchain_core.prompts import PipelinePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_community.vectorstores import FAISS
# Импортируем и класс, и сам созданный экземпляр настроек settings
from config import Settings, settings

logger = logging.getLogger(__name__)

import re
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

# читаем txt вместо json
def load_prompt_from_txt(file_path: str | Path) -> ChatPromptTemplate:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'\[(SYSTEM|HUMAN|AI)\]\s*(.*?)(?=\n\s*\[(?:SYSTEM|HUMAN|AI)\]|$)'
    matches = re.findall(pattern, content, re.DOTALL)

    messages = []
    for role, text in matches:
        role_lower = role.lower()
        cleaned = text.strip()
        if cleaned:
            messages.append((role_lower, cleaned))

    if not messages:
        raise ValueError(f"Не найдено секций [SYSTEM]/[HUMAN] в {file_path}")

    return ChatPromptTemplate.from_messages(messages)

ANSWER_PROMPT = load_prompt_from_txt("prompts/answer_prompt.txt")

class RAGService:
    """Скелет, где нужно реализовать шаги RAG."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @cached_property
    def embeddings(self) -> HuggingFaceEndpointEmbeddings:
        """
        Актуальные эмбеддинги с использованием модели BAAI/bge-m3.
        Работает на бесплатном Serverless API без конфликтов валидации.
        """
        return HuggingFaceEndpointEmbeddings(
            model="BAAI/bge-m3",  # Передаем напрямую или через self.settings.hf_embedding_model
            task="feature-extraction",  # Идеально совпадает и с Pydantic, и с сервером HF
            huggingfacehub_api_token=self.settings.hf_token
        )


    @cached_property
    def retriever(self):
        """Загрузка локального FAISS индекса и создание поисковика."""
        store = FAISS.load_local(
            folder_path=str(self.settings.vector_store_path),
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True,
        )
        return store.as_retriever(
            search_kwargs={"k": self.settings.top_k_results}
        )

    @cached_property
    def llm(self) -> GigaChat:
        """Инициализация актуального класса GigaChat."""
        return GigaChat(
            credentials=self.settings.gigachat_credentials,
            scope=self.settings.gigachat_scope,
            model=self.settings.gigachat_model,
            verify_ssl_certs=self.settings.gigachat_verify_ssl,
            temperature=0.1
        )

    @cached_property
    def chain(self):
        def format_docs(docs):
            return "\n---\n".join(doc.page_content for doc in docs)

        retrieve_step = RunnableParallel(
            question=lambda x: x["question"],
            documents=lambda x: self.retriever.invoke(x["question"]),
            history=lambda x: x.get("history", ""),  # исправлено
        )

        answer_step = (
                {
                    "context": lambda x: format_docs(x["documents"]),
                    "history": lambda x: x["history"],
                    "question": lambda x: x["question"],
                }
                | ANSWER_PROMPT
                | self.llm
                | StrOutputParser()
        )

        full_chain = retrieve_step | {
            "answer": answer_step,
            "source_documents": lambda x: x["documents"],
        }
        return full_chain

    async def ask(self, question: str, history: List[Tuple[str, str]] = None) -> dict[str, Any]:
        # Форматируем историю для промпта
        history_text = ""
        if history:
            # Берём последние 5 сообщений для контекста
            recent = history[-5:] if len(history) > 5 else history
            history_text = "\n".join([
                f"{'Пользователь' if role == 'user' else 'Ассистент'}: {msg}"
                for role, msg in recent
            ])

        # Передаём историю в цепочку
        return await self.chain.ainvoke({
            "question": question,
            "history": history_text  # Добавляем новое поле
        })
__all__ = ["RAGService"]
