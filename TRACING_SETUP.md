# Distributed Tracing для Cinema System

## Обзор

Реализована система distributed tracing с использованием OpenTelemetry и Jaeger для мониторинга запросов между микросервисами онлайн-кинотеатра.

## Архитектура трейсинга

### Компоненты

1. **Jaeger** - система сбора и визуализации трейсов
2. **OpenTelemetry** - инструментирование приложений
3. **Общий модуль трейсинга** - централизованная настройка

### Инструментированные сервисы

-   `auth_service` (порт 8000) - аутентификация и авторизация
-   `main_service` (порт 8001) - основной API
-   `log_service` (порт 8002) - сбор логов
-   `etl_service` (порт 8003) - ETL процессы

## Настройка

### 1. Jaeger

```yaml
jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: cinema_jaeger
    environment:
        - COLLECTOR_OTLP_ENABLED=true
        - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    ports:
        - "16686:16686" # Jaeger UI
        - "14268:14268" # HTTP collector
        - "14250:14250" # gRPC collector
        - "4317:4317" # OTLP gRPC receiver
        - "4318:4318" # OTLP HTTP receiver
        - "9411:9411" # Zipkin compatible endpoint
```

### 2. OpenTelemetry зависимости

```txt
opentelemetry-api~=1.21.0
opentelemetry-sdk~=1.21.0
opentelemetry-exporter-jaeger~=1.21.0
opentelemetry-exporter-otlp~=1.21.0
opentelemetry-instrumentation-fastapi~=0.42b0
opentelemetry-instrumentation-requests~=0.42b0
opentelemetry-instrumentation-aiohttp-client~=0.42b0
opentelemetry-instrumentation-sqlalchemy~=0.42b0
opentelemetry-instrumentation-redis~=0.42b0
opentelemetry-instrumentation-elasticsearch~=0.42b0
```

### 3. Общий модуль трейсинга

Создан модуль `shared/tracing/tracer.py` с классом `CinemaTracer`:

```python
from shared.tracing.tracer import get_tracer

# Инициализация трейсинга
tracer = get_tracer("service_name", "1.0.0")
tracer.initialize()

# Инструментирование приложения
tracer.instrument_all(app=app, sqlalchemy_engine=engine)
```

### 4. Переменные окружения

Каждый сервис настроен с переменными:

```yaml
environment:
    - JAEGER_OTLP_ENDPOINT=http://jaeger:4317
    - ENVIRONMENT=development
```

## Возможности

### Автоматическое инструментирование

-   **FastAPI** - HTTP запросы и ответы
-   **SQLAlchemy** - запросы к базе данных
-   **Redis** - операции с кешем
-   **Elasticsearch** - поисковые запросы
-   **HTTP клиенты** - внешние API вызовы

### Кастомные спаны

```python
from shared.tracing.tracer import get_current_span, get_trace_id

# Получение текущего трейса
trace_id = get_trace_id()

# Создание кастомного спана
with tracer.create_span("custom_operation") as span:
    tracer.add_span_attributes(span, {
        "user_id": user_id,
        "operation": "data_processing"
    })
    # Ваш код
```

### Health endpoints с trace_id

Каждый сервис имеет health endpoint, возвращающий trace_id:

```json
{
    "status": "healthy",
    "service": "main_service",
    "trace_id": "abc123..."
}
```

## Доступ к Jaeger UI

-   **URL**: http://localhost:16686
-   **Интерфейс**: Веб-интерфейс для поиска и анализа трейсов

### Основные функции Jaeger UI

1. **Поиск трейсов** по сервисам, операциям, тегам
2. **Визуализация** временной диаграммы запросов
3. **Анализ производительности** и узких мест
4. **Корреляция** между сервисами

## Мониторинг

### Метрики трейсинга

-   Количество спанов по сервисам
-   Время выполнения операций
-   Частота ошибок
-   Зависимости между сервисами

### Алерты

Можно настроить алерты на:

-   Высокую латентность
-   Частые ошибки
-   Недоступность сервисов

## Примеры использования

### 1. Отслеживание пользовательского запроса

```bash
# Запрос к API
curl http://localhost:8001/movies/

# В Jaeger UI найти трейс по:
# - Service: main_service
# - Operation: GET /movies/
```

### 2. Анализ ETL процесса

```bash
# Запуск ETL задачи
curl -X POST http://localhost:8003/etl/tmdb/popular

# Отслеживание в Jaeger:
# - Service: etl_service
# - Tags: job_id, batch_size
```

### 3. Межсервисные вызовы

Трейсы автоматически связывают запросы между сервисами:

-   main_service → auth_service (проверка токена)
-   etl_service → main_service (сохранение данных)
-   log_service → elasticsearch (индексация логов)

## Лучшие практики

### 1. Именование спанов

-   Используйте понятные имена операций
-   Включайте HTTP методы и пути
-   Добавляйте контекст (user_id, resource_id)

### 2. Атрибуты спанов

```python
span.set_attribute("user.id", user_id)
span.set_attribute("movie.id", movie_id)
span.set_attribute("operation.type", "database_query")
```

### 3. Обработка ошибок

```python
try:
    # Операция
    pass
except Exception as e:
    span.set_status(Status(StatusCode.ERROR, str(e)))
    span.record_exception(e)
    raise
```

## Производительность

### Настройки для production

```python
# Семплирование трейсов (10%)
tracer_provider = TracerProvider(
    sampler=TraceIdRatioBased(0.1)
)

# Батчевая отправка
span_processor = BatchSpanProcessor(
    otlp_exporter,
    max_queue_size=2048,
    max_export_batch_size=512
)
```

### Мониторинг overhead

-   Трейсинг добавляет ~1-5% overhead
-   Используйте семплирование в production
-   Мониторьте размер очередей экспорта

## Troubleshooting

### Проблемы с подключением

```bash
# Проверка Jaeger
curl http://localhost:16686

# Проверка OTLP endpoint
curl http://localhost:4317
```

### Отсутствие трейсов

1. Проверьте переменные окружения
2. Убедитесь в инициализации трейсера
3. Проверьте сетевое подключение к Jaeger

### Производительность

1. Настройте семплирование
2. Оптимизируйте размер батчей
3. Мониторьте память и CPU

## Заключение

Система distributed tracing обеспечивает:

-   **Видимость** в работу микросервисов
-   **Диагностику** проблем производительности
-   **Мониторинг** межсервисных взаимодействий
-   **Отладку** сложных сценариев

Трейсинг является критически важным компонентом для поддержки и развития микросервисной архитектуры онлайн-кинотеатра.
