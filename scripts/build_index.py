#!/usr/bin/env python3
"""Учебный скрипт для построения FAISS индекса."""

from __future__ import annotations
import json
import argparse
import pathlib

# Исправленные импорты из актуальных пакетов
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from src.config import settings
from src.rag_service import RAGService


def load_dataset(path: pathlib.Path) -> list[Document]:
    """Прочитать JSON и превратить каждую запись в Document."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return [
        Document(
            page_content=f"Вопрос: {item['question']}\n\nОтвет: {item['answer']}"
        )
        for item in data
    ]

def build_index(input_path: pathlib.Path, store_dir: pathlib.Path) -> None:
    """Создать сплиттер, посчитать эмбеддинги и сохранить индекс."""
    documents = load_dataset(input_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(documents)

    # Используем RAGService для получения настроенной модели эмбеддингов
    service = RAGService(settings)

    # Передаем chunks и объект эмбеддингов HuggingFaceEndpointEmbeddings
    store = FAISS.from_documents(chunks, service.embeddings)
    store.save_local(str(store_dir))

def main() -> None:
    # Добавлены аргументы --input и --store
    parser = argparse.ArgumentParser(description="FAISS builder")

    parser.add_argument(
        "--input",
        type=pathlib.Path,
        required=True,
        help="JSON-файл с датасетом",
    )
    parser.add_argument(
        "--store",
        type=pathlib.Path,
        required=True,
        help="Каталог для сохранения FAISS",
    )

    args = parser.parse_args()

    build_index(args.input, args.store)

if __name__ == "__main__":
    main()
