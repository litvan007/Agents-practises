import os
import subprocess
import sys


def find_project_root(current_dir, target_file="pyproject.toml"):
    """Рекурсивно ищет вверх по дереву папок корень проекта, где лежит pyproject.toml."""
    while True:
        if os.path.exists(os.path.join(current_dir, target_file)):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Дошли до корня диска
            return None
        current_dir = parent_dir


def main():
    # Определяем, где лежит этот скрипт run.py
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Ищем корень, где находится poetry окружение
    root_dir = find_project_root(script_dir)

    if not root_dir:
        print(
            "Ошибка: Не удалось найти корень проекта с файлом pyproject.toml!"
        )
        sys.exit(1)

    # Меняем рабочую директорию на корень проекта
    os.chdir(root_dir)

    # Команда, которую нужно выполнить
    cmd = [sys.executable, "-m", "poetry", "run", "python", "tg_bot_rag_faq/src/main.py"]
    print(f"-> Запуск из корня: {root_dir}")
    print(f"-> Выполняется: {' '.join(cmd)}\n")

    try:
        # Запускаем процесс и передаем ему управление терминалом
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n Процесс завершился с ошибкой: {e}")
    except KeyboardInterrupt:
        print("\n Бот остановлен пользователем (Ctrl+C).")


if __name__ == "__main__":
    main()
