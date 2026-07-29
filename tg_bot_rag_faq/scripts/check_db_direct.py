#!/usr/bin/env python3
"""Прямая проверка SQLite без зависимостей от бота."""

import sqlite3
from pathlib import Path
import sys

# Путь к БД (совпадает с src/db.py)
DB_PATH = Path(__file__).parent.parent / "storage" / "chat.db"


def main():
    print("🔍 ПРЯМАЯ ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"❌ Файл БД не найден: {DB_PATH}")
        print("   Бот ещё не запускался или БД не создана.")
        return

    print(f"✅ Файл БД найден. Размер: {DB_PATH.stat().st_size} байт")

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Проверяем наличие таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
        if not cursor.fetchone():
            print("⚠️ Таблица 'chat_history' не существует!")
            return

        # Считаем записи
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        total = cursor.fetchone()[0]
        print(f"📊 Всего записей: {total}")

        if total == 0:
            print("⚠️ Таблица пуста. Отправьте сообщения боту.")
            return

        # Показываем последние 10 записей
        print("\n📋 Последние 10 записей (от новых к старым):")
        print("-" * 60)
        cursor.execute("""
                       SELECT id, user_id, role, message, timestamp
                       FROM chat_history
                       ORDER BY timestamp DESC
                           LIMIT 10
                       """)
        for row in cursor.fetchall():
            print(f"ID: {row[0]} | User: {row[1]} | Role: {row[2]}")
            print(f"    Сообщение: {row[3][:100]}{'...' if len(row[3]) > 100 else ''}")
            print(f"    Время: {row[4]}")
            print("-" * 40)

        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Ошибка SQLite: {e}")


if __name__ == "__main__":
    main()