import os

# Список папок и файлов, которые нужно игнорировать (чтобы не забивать контекст LLM)
EXCLUDE_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.idea', '.vscode', 'dist', 'build', '.venv-poetry', '.ruff_cache'}
EXCLUDE_FILES = {'.DS_Store', 'generate_tree.py', 'project_tree.txt'}


def generate_tree(dir_path, prefix=""):
    tree_str = ""
    try:
        # Получаем список всех элементов в директории
        items = sorted(os.listdir(dir_path))
    except PermissionError:
        return ""

    # Фильтруем игнорируемые элементы
    items = [item for item in items if item not in EXCLUDE_DIRS and item not in EXCLUDE_FILES]

    for i, item in enumerate(items):
        path = os.path.join(dir_path, item)
        is_last = (i == len(items) - 1)

        # Выбираем правильные символы для дерева
        connector = "└── " if is_last else "├── "
        tree_str += f"{prefix}{connector}{item}\n"

        # Если это папка, уходим в рекурсию
        if os.path.isdir(path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            tree_str += generate_tree(path, new_prefix)

    return tree_str


if __name__ == "__main__":
    current_dir = os.getcwd()
    project_name = os.path.basename(current_dir)

    # Формируем итоговый текст
    output_text = f"Структура проекта: {project_name}\n\n"
    output_text += generate_tree(current_dir)

    # Записываем результат в файл
    output_file = "project_tree.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"Готово! Структура проекта сохранена в файл: {output_file}")
