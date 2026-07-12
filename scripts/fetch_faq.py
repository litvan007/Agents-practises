#!/usr/bin/env python3
"""Учебный скрипт для скачивания HTML FAQ."""

from __future__ import annotations

import argparse
import pathlib
from http.client import responses

import requests


def download(url: str, output: pathlib.Path, verify: bool = True) -> None:
    """TODO: выполните GET запрос и сохраните текст."""
    response=requests.get(url, verify = verify)
    response.raise_for_status()
    output.write_text(response.text, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Загрузка FAQ страницы")
    # TODO: добавьте аргументы --url, --out, --no-verify
    parser.add_argument(
        "--url",
        required=True,
        help="URL страницы для загрузки"
    )

    parser.add_argument(
        "--out",
        required=True,
        type=pathlib.Path,
        help="Путь к выходному файлу"
    )

    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Отключить проверку SSL сертификата"
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    download("TODO", pathlib.Path("TODO"))


if __name__ == "__main__":
    main()
