# ставим урезанный лёгкий пайтон slim
FROM python:3.12-slim

# Системные зависимости (для faiss-cpu и др.) из за лёгкой версии пайтона slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make \
    libblas-dev liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем UV из официального образа
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ставим как рабочую папку app, в некй будут выполнятся все команды copy run cmd
WORKDIR /app

# копируем файлы зависимостей в рабочую папку для кэширования слоёв чтобы не переустанавливать пакеты каждый раз если не изменений
COPY pyproject.toml uv.lock ./

# установка зависимостей с кэшированием через BuildKit и настроками frozen nodev  noinstallproject
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# копируем все папки и файлы из проекта
COPY . .
# устанавливаем три переменные окружения, запрет на .pyc для экономии места, включаем логи в колнсоль, ставим path чтобы команды запускались из указания полного пути
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}"
# команда по умолчанию, которая выполняется при старте контейнера. запускает бота.
CMD ["python", "tg_bot_rag_faq/src/main.py"]