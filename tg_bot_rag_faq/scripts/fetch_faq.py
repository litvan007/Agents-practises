#!/usr/bin/env python3
"""Учебный скрипт для скачивания HTML FAQ."""

from __future__ import annotations

import argparse
import pathlib

import requests


def download(url: str, output: pathlib.Path, verify: bool = True) -> None:
    """TODO: выполните GET запрос и сохраните текст."""
    raise NotImplementedError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Загрузка FAQ страницы")
    # TODO: добавьте аргументы --url, --out, --no-verify
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    download("TODO", pathlib.Path("TODO"))


if __name__ == "__main__":
    main()
