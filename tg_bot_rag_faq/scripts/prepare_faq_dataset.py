#!/usr/bin/env python3
"""Учебный конвертер FAQ в JSON."""

from __future__ import annotations

import argparse
import json
import pathlib

from bs4 import BeautifulSoup


def parse_html(path: pathlib.Path) -> list[dict[str, str]]:
    """TODO: верните список словарей question/answer."""
    raise NotImplementedError


def parse_markdown(path: pathlib.Path) -> list[dict[str, str]]:
    """TODO: реализуйте парсинг заголовков вида ## Вопрос."""
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser(description="Сбор датасета")
    # TODO: добавьте аргументы --html, --markdown, --out
    args = parser.parse_args()
    # TODO: в зависимости от аргументов вызовите parse_html / parse_markdown
    # TODO: сохраните JSON (используйте json.dump)
    raise NotImplementedError


if __name__ == "__main__":
    main()
