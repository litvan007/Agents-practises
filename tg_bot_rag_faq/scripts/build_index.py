#!/usr/bin/env python3
"""Учебный скрипт для построения FAISS индекса."""

from __future__ import annotations

import argparse
import pathlib

from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GigaChatEmbeddings
from langchain_community.vectorstores import FAISS


def load_dataset(path: pathlib.Path) -> list[Document]:
    """TODO: прочитайте JSON и превратите каждую запись в Document."""
    raise NotImplementedError


def build_index(input_path: pathlib.Path, store_dir: pathlib.Path) -> None:
    """TODO: создайте сплиттер, посчитайте эмбеддинги и сохраните индекс."""
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser(description="FAISS builder")
    # TODO: добавьте аргументы --input и --store
    raise NotImplementedError


if __name__ == "__main__":
    main()
