# Cinema Project - Локальное файловое хранилище с MinIO

## Обзор

Проект теперь использует локальное S3-совместимое хранилище MinIO вместо внешних S3 сервисов. Это обеспечивает:

-   ✅ Полную автономность разработки
-   ✅ Быструю работу с файлами
-   ✅ S3-совместимый API
-   ✅ Веб-интерфейс для управления файлами
-   ✅ Простое развертывание

## Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │     MinIO       │    │   PostgreSQL    │
│   (Port 8001)   │◄──►│  (Port 9000)    │    │   (Port 5432)   │
│                 │    │                 │    │                 │
│ - File API      │    │ - File Storage  │    │ - Metadata      │
│ - Movie API     │    │ - Web Console   │    │ - Movie URLs    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Быстрый старт

### 1. Запуск всех сервисов

```bash
cd cinema2
docker-compose up -d
```

Это запустит:

-   PostgreSQL (порт 5432)
-   Redis (порт 6379)
-   Elasticsearch (порт 9200)
-   Kibana (порт 5601)
-   MinIO (порт 9000, консоль 9001)
-   Auth Service (порт 8000)
-   Main Service (порт 8001)
-   Log Service (порт 8002)

### 2. Проверка работы MinIO

Откройте веб-консоль MinIO: http://localhost:9001

Логин: `minioadmin`
Пароль: `minioadmin123`

### 3. Применение миграций

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Примените миграции
alembic upgrade head
```

### 4. Заполнение MinIO данными

```bash
# Запустите скрипт заполнения
python minio_filling.py
```

## API Endpoints

### Файловые операции

-   `POST /files/upload` - Загрузка файла
-   `POST /files/upload-image-from-url` - Загрузка изображения по URL
-   `GET /files/download/{file_path}` - Скачивание файла
-   `DELETE /files/delete/{file_path}` - Удаление файла
-   `GET /files/list` - Список файлов
-   `GET /files/url/{file_path}` - Получение URL файла

### Фильмы

-   `GET /movies/` - Список фильмов
-   `GET /movies/{id}` - Фильм по ID

## Веб-интерфейс

Файловый менеджер доступен по адресу: http://localhost:8001/static/file_manager.html

Функции:

-   Загрузка файлов
-   Загрузка изображений по URL
-   Просмотр списка файлов
-   Удаление файлов
-   Получение прямых ссылок

## Структура файлов в MinIO

```
cinema-files/
├── movies/
│   ├── 1/
│   │   ├── poster.jpg
│   │   ├── trailer.mp4
│   │   └── metadata.json
│   ├── 2/
│   │   ├── poster.jpg
│   │   └── metadata.json
│   └── ...
├── uploads/
│   ├── user_file1.pdf
│   └── user_file2.jpg
└── images/
    ├── banner1.jpg
    └── logo.png
```

## Конфигурация

### Переменные окружения

```env
# MinIO настройки
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=cinema-files
```

### Настройки в коде

```python
# main_service/config.py
def get_minio_settings():
    return {
        "endpoint": settings.MINIO_ENDPOINT,
        "access_key": settings.MINIO_ACCESS_KEY,
        "secret_key": settings.MINIO_SECRET_KEY,
        "bucket": settings.MINIO_BUCKET
    }
```

## Модель данных

### Обновленная модель Movie

```python
class Movie(Base):
    title: Mapped[str_null_true]
    description: Mapped[str] = mapped_column(Text)
    release_date: Mapped[Date] = mapped_column(Date)
    duration: Mapped[int] = mapped_column(Integer)
    rating: Mapped[int] = mapped_column(Integer)
    movie_url: Mapped[str_null_true]
    poster_url: Mapped[str_null_true]  # URL постера в MinIO
    trailer_url: Mapped[str_null_true]  # URL трейлера в MinIO
```

## Полезные команды

### Работа с MinIO CLI (опционально)

```bash
# Установка MinIO Client
brew install minio/stable/mc

# Настройка алиаса
mc alias set local http://localhost:9000 minioadmin minioadmin123

# Просмотр файлов
mc ls local/cinema-files

# Копирование файла
mc cp file.jpg local/cinema-files/uploads/
```

### Мониторинг

```bash
# Логи MinIO
docker logs cinema_minio

# Логи Main Service
docker logs main_service

# Статус контейнеров
docker-compose ps
```

## Troubleshooting

### MinIO не запускается

1. Проверьте, что порты 9000 и 9001 свободны
2. Убедитесь, что Docker имеет достаточно ресурсов
3. Проверьте логи: `docker logs cinema_minio`

### Ошибки подключения к MinIO

1. Убедитесь, что MinIO запущен: `docker-compose ps`
2. Проверьте настройки в `config.py`
3. Убедитесь, что bucket создан

### Проблемы с загрузкой файлов

1. Проверьте права доступа к папкам
2. Убедитесь, что размер файла не превышает лимиты
3. Проверьте логи сервиса: `docker logs main_service`

## Преимущества локального MinIO

1. **Скорость**: Нет задержек сети
2. **Надежность**: Полный контроль над данными
3. **Разработка**: Работа без интернета
4. **Тестирование**: Изолированная среда
5. **Совместимость**: S3 API для легкой миграции

## Миграция с внешнего S3

Если у вас есть данные во внешнем S3, вы можете их перенести:

```bash
# Синхронизация с внешним S3
mc mirror s3-external/bucket local/cinema-files
```

## Безопасность

В продакшене рекомендуется:

1. Изменить стандартные логин/пароль MinIO
2. Настроить HTTPS
3. Ограничить доступ к консоли MinIO
4. Настроить backup политики

## Дополнительные возможности

-   Версионирование файлов
-   Lifecycle политики
-   Репликация
-   Шифрование
-   Интеграция с CDN
