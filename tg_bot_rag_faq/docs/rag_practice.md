# Теория и практика RAG для Telegram-бота

Этот документ — теоретический компаньон к пошаговому уроку `docs/rag_lesson_plan.md`. Здесь собраны ключевые идеи Retrieval-Augmented Generation (RAG), ссылки на код и материалы, которые помогают понять архитектуру прежде, чем приступать к выполнению задач.

## 1. Что такое RAG
RAG — это способ ответить на вопрос пользователя, сочетая языковую модель (LLM) и базу знаний:
1. **Retrieval** — ищем релевантные документы в индексе (обычно векторном).
2. **Augmentation** — добавляем найденные фрагменты в промпт для LLM.
3. **Generation** — модель формирует ответ, опираясь на полученный контекст.

Преимущества: ответы точнее (LLM опирается на достоверные факты), легче обновлять знания (индекс можно перестроить без дообучения модели), проще объяснить источник информации.

## 2. Архитектура проекта
Схема компонентов из `src/`:
- `config.py` — загрузка настроек из `.env`, чтобы удобно переключать токены, пути и параметры индекса.
- `rag_service.py` — реализация RAG пайплайна (LLM + retriever + промпты).
- `bot.py` — Telegram-обработчики: принимает текст от пользователя, вызывает RAG и возвращает ответ.

Вспомогательные скрипты из `scripts/` помогают сформировать датасет (`prepare_faq_dataset.py`) и построить FAISS индекс (`build_index.py`).

## 3. LangChain шаг за шагом
Разберём основной код (см. `src/rag_service.py`).

### 3.1. Инициализация эмбеддингов и индекса
```python
self.embeddings = GigaChatEmbeddings(...)
self.retriever = FAISS.load_local(...).as_retriever(k=TOP_K)
```
1. **Эмбеддинги** переводят текст в векторы; LangChain уже знает, как говорить с GigaChat.
2. **FAISS retriever** — поиск ближайших фрагментов по косинусному расстоянию.

### 3.2. Логика генерации ответа
```python
ANSWER_PROMPT = ChatPromptTemplate.from_messages([...])
answer_chain = ANSWER_PROMPT | llm | StrOutputParser()
```
1. **PromptTemplate** описывает системные инструкции.
2. Через оператор `|` (LCEL) цепляем шаблон к модели и берём только текст ответа.

### 3.3. Соединяем Retrieval + Generation
```python
def _invoke(payload):
    question = payload["question"]
    documents = self.retriever.invoke(question)
    context = "\n\n---\n\n".join(doc.page_content for doc in documents)
    answer = answer_chain.invoke({"context": context, "question": question})
    return {"answer": answer, "source_documents": documents}
```
1. Получаем вопрос.
2. Ищем документы (`retriever.invoke`).
3. Склеиваем контекст и передаём в промпт.
4. Возвращаем ответ + исходные документы (бот выводит источники).

## 4. Что полезно понимать перед практикой
- **Формат данных.** Скрипт `scripts/prepare_faq_dataset.py` превращает HTML/Markdown в JSON со структурой `{"question": "...", "answer": "...", "source": "..."}`. Эти поля позже попадают в `Document`.
- **Конструктор Document.** В `scripts/build_index.py` каждая запись оборачивается в `Document(page_content=..., metadata=...)`. `metadata["source"]` потом используется ботом, чтобы показывать ссылки на оригинальные материалы.
- **LCEL (LangChain Expression Language).** Это способ собирать цепочки через оператор `|`. Мини-пример:
    ```python
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableLambda

    prompt = ChatPromptTemplate.from_template("Перефразируй: {text}")
    chain = prompt | llm
    chain.invoke({"text": "Где мой FAQ?"})
    ```
- **Vector Store vs Retriever.** `FAISS` хранит вектора и отвечает на запросы ближайших соседей. Метод `as_retriever(k=TOP_K)` возвращает абстракцию, которая прозрачно интегрируется в цепочки LangChain.
- **Промпт-инжиниринг.** Посмотрите на `ANSWER_PROMPT` в `src/rag_service.py`: системное сообщение задаёт стиль, а человек передаёт контекст и вопрос. Отдельный «condense prompt» можно добавить позже, чтобы учитывать историю диалога.

## 5. Как улучшать базовый RAG
В `README.md` описаны идеи с учётом истории диалога и LCEL пайплайнов. Кратко:
- Добавьте `CONDENSE_PROMPT` и конденсируйте вопрос перед поиском.
- Соберите полноценный pipeline через `RunnableParallel`, чтобы хранить промежуточные значения.
- Вставьте фильтры: если релевантных документов мало, говорите «не знаю».

## 6. Что почитать дальше
- [LangChain — Quickstart](https://python.langchain.com/docs/get_started/quickstart)
- [FAISS basics](https://github.com/facebookresearch/faiss/wiki)
- Документация GigaChat API для уточнения параметров моделей.

Этого достаточно, чтобы уверенно разобраться в коде `rag_service.py`, адаптировать его под собственный FAQ и экспериментировать с улучшениями RAG.
