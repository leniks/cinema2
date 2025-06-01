# 🐳 Docker Setup для Онлайн Кинотеатра

## Архитектура

Проект состоит из следующих сервисов:

-   **Frontend** (React + Nginx) - порт 3000
-   **Auth Service** (FastAPI) - порт 8000
-   **Main Service** (FastAPI) - порт 8001
-   **Log Service** (FastAPI) - порт 8002
-   **PostgreSQL** - порт 5432
-   **Redis** - порт 6379
-   **Elasticsearch** - порт 9200
-   **Kibana** - порт 5601
-   **MinIO S3** - порт 9000 (API), 9001 (Console)

## 🚀 Быстрый запуск

```bash
# Клонируем репозиторий
git clone <repository-url>
cd cinema2

# Запускаем все сервисы
docker-compose up -d

# Проверяем статус
docker-compose ps
```

## 📱 Доступ к сервисам

-   **Фронтенд**: http://localhost:3000
-   **API документация (Main)**: http://localhost:8001/docs
-   **API документация (Auth)**: http://localhost:8000/docs
-   **API документация (Log)**: http://localhost:8002/docs
-   **Kibana**: http://localhost:5601
-   **MinIO Console**: http://localhost:9001
-   **Elasticsearch**: http://localhost:9200

## 🔧 Настройка данных

### 1. Заполнение S3 фильмами

```bash
# Заходим в контейнер main_service
docker exec -it main_service bash

# Запускаем скрипт заполнения
python fill_s3_with_movies.py
```

### 2. Индексация в Elasticsearch

```bash
# Индексируем фильмы
python index_movies_to_elasticsearch.py
```

## 🛠️ Разработка

### Пересборка отдельного сервиса

```bash
# Пересобрать только фронтенд
docker-compose build frontend
docker-compose up -d frontend

# Пересобрать бекенд сервисы
docker-compose build main_service auth_service log_service
docker-compose up -d main_service auth_service log_service
```

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f frontend
docker-compose logs -f main_service
```

### Остановка и очистка

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (ВНИМАНИЕ: удалит все данные!)
docker-compose down -v

# Очистить неиспользуемые образы
docker system prune -f
```

## 🔍 Отладка

### Проверка подключений

```bash
# Проверить доступность API
curl http://localhost:8001/health
curl http://localhost:8000/health

# Проверить Elasticsearch
curl http://localhost:9200/_cluster/health

# Проверить MinIO
curl http://localhost:9000/minio/health/live
```

### Подключение к базе данных

```bash
docker exec -it cinema_db psql -U admin -d cinema
```

### Подключение к Redis

```bash
docker exec -it cinema_redis redis-cli
```

## 📝 Переменные окружения

Основные переменные настроены в `docker-compose.yml`:

-   `REACT_APP_API_URL` - URL основного API
-   `REACT_APP_AUTH_URL` - URL сервиса аутентификации
-   `REACT_APP_MINIO_URL` - URL MinIO
-   `DB_HOST`, `DB_PORT`, `DB_NAME` - настройки БД
-   `REDIS_HOST`, `REDIS_PORT` - настройки Redis
-   `ELASTICSEARCH_HOST` - настройки Elasticsearch

## 🚨 Troubleshooting

### Проблемы с памятью Elasticsearch

```bash
# Увеличить vm.max_map_count на хосте
sudo sysctl -w vm.max_map_count=262144
```

### Проблемы с правами доступа

```bash
# Исправить права на volumes
sudo chown -R $USER:$USER ./data
```

### Очистка и перезапуск

```bash
# Полная очистка и перезапуск
docker-compose down -v
docker system prune -f
docker-compose up -d
```
