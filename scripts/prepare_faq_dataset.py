#!/usr/bin/env python3
"""Учебный конвертер FAQ в JSON."""

from __future__ import annotations

import argparse
import json
import pathlib

from bs4 import BeautifulSoup


def parse_html(path: pathlib.Path) -> list[dict[str, str]]:
    """TODO: верните список словарей question/answer."""
    soup  = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    dataset: list[dict[str,str]] = []
    for h2 in soup.find_all("h2"):

        question = h2.get_text(strip=True)
        answer_parts=[]
        node = h2.find_next_sibling()

        while node is not None and node.name != "h2":
            text=node.get_text(" ", strip=True)
            if text:
                answer_parts.append(text)
            node = node.find_next_sibling()

        answer = "\n".join(answer_parts).strip()
        if question and answer:
            dataset.append(
                {
                    "question": question,
                    "answer": answer,
                }

            )
    return dataset
def parse_markdown(path: pathlib.Path) -> list[dict[str, str]]:
    """TODO: реализуйте парсинг заголовков вида ## Вопрос."""
    lines=path.read_text(encoding='utf=8').splitlines()
    dataset: list[dict[str,str]]=[]
    question: str | None = None
    answer_lines: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if question is not None:
                dataset.append(
                    {
                        "question": question,
                        "answer": "\n".join(answer_lines).strip(),
                    }
                )

            question = line[3:].strip()
            answer_lines = []
        else:
            if question is not None:
                answer_lines.append(line)

    if question is not None:
        dataset.append(
            {
                "question": question,
                "answer": "\n".join(answer_lines).strip(),
            }
        )

    return dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Сбор датасета")
    # TODO: добавьте аргументы --html, --markdown, --out
    parser.add_argument("--html", type=pathlib.Path)
    parser.add_argument("--markdown", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path, required=True)

    args = parser.parse_args()
    # TODO: в зависимости от аргументов вызовите parse_html / parse_markdown
    # TODO: сохраните JSON (используйте json.dump)
    if args.html:
        dataset = parse_html(args.html)
    elif args.markdown:
        dataset = parse_markdown(args.markdown)
    else:
        parser.error("Необходимо указать --html или --markdown")

    with args.out.open("w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)



if __name__ == "__main__":
    main()
