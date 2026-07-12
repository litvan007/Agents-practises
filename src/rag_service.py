"""Учебная версия RAG сервиса. Заполните пропуски."""

from __future__ import annotations

import logging
from functools import cached_property
from typing import Any

# Новые раздельные пакеты для aполной совместимости
from langchain_gigachat.chat_models import GigaChat
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.prompts import ChatPromptTemplate

# Вместо: from langchain_core.prompts import PipelinePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_community.vectorstores import FAISS
# Импортируем и класс, и сам созданный экземпляр настроек settings
from .config import Settings, settings

logger = logging.getLogger(__name__)


ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", """
        Ты — полезный ассистент. 
        Отвечай на вопросы пользователя, используя только предоставленный контекст.
        Если в контексте нет необходимой информации, сообщи об этом и не придумывай ответ.
        
        Контекст:
        {context}
        """),
        ("human", """
        Вопрос пользователя:
        {question}
        """),
    ]
)


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
        logger.info("TODO: соберите базовую цепочку")
        answer_chain = ANSWER_PROMPT | self.llm | StrOutputParser()

        def _invoke(payload: dict[str, Any]):
            # 1. Достаньте вопрос из payload
            question=payload['question']
            # 2. Получите документы через retriever
            documents=self.retriever.invoke(question)
            # 3. Соберите строку контекста ("\n---\n".join(...))
            context="\n---\n".join(doc.page_content for doc in documents)
            # 4. Вызовите answer_chain
            answer=answer_chain.invoke({
                "context": context,
                "question": question,}
            )
            # 5. Верните dict с ключами answer и source_documents
            return {
                    'answer':answer,
                    "source_documents":documents
                    }
            raise NotImplementedError

        return RunnableLambda(_invoke)

    async def ask(self, question: str) -> dict[str, Any]:
        return self.chain.invoke({"question": question})


__all__ = ["RAGService"]
