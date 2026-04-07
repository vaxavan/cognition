# 🧠 Cognition Project

> Production-ready микросервисная архитектура для RAG (Retrieval-Augmented Generation) и чат-ботов с обработкой документов.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Оглавление

- [✨ Особенности](#-особенности)
- [🏗️ Архитектура](#️-архитектура)
- [🚀 Быстрый старт](#-быстрый-старт)
- [🔧 Настройка окружения](#-настройка-окружения)
- [🧪 Тестирование](#-тестирование)
- [📁 Структура проекта](#-структура-проекта)
- [🐳 Docker (опционально)](#-docker-опционально)
- [🤝 Вклад в проект](#-вклад-в-проект)
- [📄 Лицензия](#-лицензия)

---

## ✨ Особенности

- 🔹 **Микросервисная архитектура**: Разделение на `chat-service` (оркестрация) и `context-engine` (обработка файлов)
- 🔹 **Поддержка форматов**: Парсинг PDF, DOCX, TXT, MD с автоматическим определением типа
- 🔹 **Асинхронность**: Полностью асинхронный стек на базе `asyncio` и `FastAPI`
- 🔹 **Хранилище**: Интеграция с MinIO (S3-compatible) для загрузки файлов через presigned URLs
- 🔹 **База данных**: SQLAlchemy + SQLite (легко заменяется на PostgreSQL)
- 🔹 **Безопасность**: Подготовка к JWT-авторизации, валидация через Pydantic v2
- 🔹 **Тестируемость**: Встроенные тесты и мок-режим для разработки без внешних зависимостей

---

## 🏗️ Архитектура

```
┌─────────────────┐
│   Frontend      │
│   (React/HTML)  │
└────────┬────────┘
         │ HTTP/JSON
         ▼
┌─────────────────┐
│  Chat Service   │  ← Порт 8000
│  (FastAPI)      │
│  • Регистрация  │
│  • Presigned URL│
│  • Оркестрация  │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│ Context Engine  │  ← Порт 8002
│  (FastAPI)      │
│  • Парсинг      │
│  • Чанкинг      │
│  • Векторизация │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────────┐
│  БД    │ │   MinIO    │
│ SQLite │ │ Хранилище  │
└────────┘ └────────────┘
```

### Компоненты

| Сервис | Порт | Описание |
|--------|------|----------|
| `chat-service` | 8000 | API для управления чатами, пользователями и файлами. Генерирует presigned URL для загрузки. |
| `context-engine` | 8002 | Микросервис обработки документов. Парсит файлы, разбивает на чанки, готовит контекст для LLM. |
| `MinIO` | 9000/9001 | S3-совместимое объектное хранилище для файлов. |
| `Database` | - | SQLite (по умолчанию) или PostgreSQL для хранения метаданных. |

---

## 🚀 Быстрый старт

### 1. Клонирование и установка

```bash
# Клонировать репозиторий
git clone https://github.com/vaxavan/cognition.git
cd cognition/base

# Создать виртуальное окружение
python -m venv .venv

# Активировать окружение
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2. Установка зависимостей

```bash
# Установить chat-service
cd chat-service
pip install -e .
cd ..

# Установить context-engine
cd context-engine
pip install -e .
cd ..
```

### 3. Запуск сервисов

**Окно 1 — Chat Service:**
```bash
cd chat-service
uvicorn app.main:app --reload --port 8000
```
👉 Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Окно 2 — Context Engine:**
```bash
cd context-engine
uvicorn context_engine.main:app --reload --port 8002
```
👉 Swagger UI: [http://127.0.0.1:8002/docs](http://127.0.0.1:8002/docs)

**Окно 3 — Frontend (опционально):**
```bash
cd frontend
python -m http.server 8080
```
👉 Интерфейс: [http://127.0.0.1:8080](http://127.0.0.1:8080)

### 4. Проверка работы

Открой в браузере:
- [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) → `{"status":"healthy"}`
- [http://127.0.0.1:8002/health](http://127.0.0.1:8002/health) → `{"status":"healthy"}`

---

## 🔧 Настройка окружения

### Переменные окружения (.env)

Создай файл `.env` в корне каждого сервиса на основе `.env.example`:

**chat-service/.env**:
```env
DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///./chat.db
MINIO_ENDPOINT=http://localhost:9000
MINIO_BUCKET=uploads
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
CONTEXT_ENGINE_URL=http://localhost:8002
SECRET_KEY=dev-secret-change-me-in-prod
```

**context-engine/.env**:
```env
DEBUG=true
MINIO_ENDPOINT=http://localhost:9000
MINIO_BUCKET=uploads
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
DEFAULT_CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### Запуск MinIO (локально)

**Вариант А: Docker**
```bash
docker run -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"
```
👉 Console: [http://localhost:9001](http://localhost:9001)

**Вариант Б: Скачать .exe (Windows)**
1. Скачай с [min.io/download](https://min.io/download)
2. Запусти: `.\minio.exe server data --console-address ":9001"`

---

## 🧪 Тестирование

### Запуск полного теста архитектуры

```bash
cd base
python run_all_tests.py
```

**Ожидаемый вывод:**
```
🎉 ВСЕ КРИТИЧЕСКИЕ ПРОВЕРКИ ПРОЙДЕНЫ!
✅ chat-service принимает запросы
✅ context-engine обрабатывает файлы
✅ Сервисы общаются через HTTP
✅ База данных сохраняет статусы
```

### Тестирование через Swagger

1. Открой [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Найди `POST /api/v1/files/request-upload`
3. Нажми **Try it out** → **Execute**
4. Скопируй `upload_url` и загрузи файл через `curl` или браузер

---

## 📁 Структура проекта

```
base/
├── README.md                 # Этот файл
├── .gitignore                # Исключения для Git
├── docker-compose.yml        # Оркестрация контейнеров
│
├── chat-service/             # 🗣️ Сервис чатов и файлов
│   ├── app/
│   │   ├── api/v1/           # Эндпоинты (files, chat, auth)
│   │   ├── core/             # Конфигурация, логгер
│   │   ├── models/           # SQLAlchemy модели
│   │   ├── repositories/     # Доступ к данным
│   │   ├── schemas/          # Pydantic схемы
│   │   ├── services/         # Бизнес-логика
│   │   ├── storage/          # S3/MinIO клиент
│   │   └── main.py           # Точка входа FastAPI
│   ├── pyproject.toml        # Зависимости и метаданные
│   └── chat.db               # SQLite БД (создаётся автоматически)
│
├── context-engine/           # 🧠 Движок обработки контекста
│   ├── context_engine/
│   │   ├── api/v1/routers/   # Эндпоинт /internal/process
│   │   ├── core/config.py    # Настройки
│   │   ├── models/schemas.py # Pydantic модели
│   │   ├── services/         # Парсеры (PDF, DOCX, TXT) + чанкер
│   │   ├── storage/          # S3 клиент для скачивания
│   │   └── main.py           # Точка входа
│   └── pyproject.toml
│
├── frontend/                 # 🎨 Простой интерфейс для тестов
│   ├── index.html            # Единый HTML+CSS+JS файл
│   └── README.md             # Инструкция по запуску
│
└── tools/                    # 🛠️ Утилиты (игнорируются Git)
    ├── minio.exe             # Бинарник MinIO (не коммитить!)
    └── data/                 # Данные хранилища (не коммитить!)
```

---

## 🐳 Docker (опционально)

Для запуска всего стека одной командой:

```bash
# Сборка и запуск
docker-compose up --build

# Остановка
docker-compose down
```

> ⚠️ Требуется установленный Docker Desktop.

---

## 🤝 Вклад в проект

1.  Создай форк репозитория
2.  Создай ветку для фичи (`git checkout -b feature/amazing-feature`)
3.  Закоммить изменения (`git commit -m 'Add amazing feature'`)
4.  Запушь в ветку (`git push origin feature/amazing-feature`)
5.  Открой Pull Request

### Guidelines

- ✅ Следуй [PEP 8](https://peps.python.org/pep-0008/) для кода на Python
- ✅ Добавляй типизацию (type hints) везде, где возможно
- ✅ Пиши докстринги в Google-style
- ✅ Покрывай новую логику тестами

---

## 📄 Лицензия

Распространяется под лицензией **MIT**. См. файл [LICENSE](LICENSE) для деталей.

---

## 👤 Автор

**Alice** — fullstack разработчик 🛠️

- 🔗 [GitHub](https://github.com/vaxavan)
- 💡 Идеи и предложения приветствуются!

---

> ⚠️ **Примечание для разработки**: Файлы `tools/minio.exe` и `tools/data/` намеренно исключены из репозитория через `.gitignore`. Скачайте MinIO отдельно при необходимости локального запуска хранилища.
```
