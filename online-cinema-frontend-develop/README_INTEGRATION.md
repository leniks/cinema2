# 🎬 Интеграция фронтенда с новым бекендом

## Обзор изменений

Фронтенд был адаптирован для работы с новым микросервисным бекендом на FastAPI:

### Архитектура нового бекенда:

- **Auth Service** (порт 8000) - аутентификация и авторизация
- **Main Service** (порт 8001) - основная логика, фильмы, файлы
- **MinIO** (порт 9000) - файловое хранилище
- **PostgreSQL** (порт 5432) - база данных

## Основные изменения

### 1. Конфигурация API (`src/config/api.config.ts`)

- Обновлены URL для разных сервисов
- Добавлена поддержка MinIO
- Настроен прокси для постеров

### 2. API клиент (`src/api/movie-api.ts`)

- Разделены запросы на auth и main API
- Обновлены endpoints под новую структуру
- Адаптированы модели данных
- Добавлена поддержка прокси для изображений

### 3. Аутентификация (`src/contexts/auth-context.tsx`)

- Обновлена обработка JWT токенов
- Адаптирована под новый формат ответа API
- Добавлено сохранение дополнительных данных пользователя

### 4. Интерфейсы (`src/interfaces.ts`)

- Добавлены интерфейсы для нового бекенда
- Обновлены типы для совместимости

## Запуск

### Быстрый старт

```bash
# Запуск с правильными настройками
./start-with-new-backend.sh
```

### Ручной запуск

```bash
# Установка зависимостей
yarn install

# Установка переменных окружения
export REACT_APP_API_URL=http://localhost:8001
export REACT_APP_AUTH_URL=http://localhost:8000
export REACT_APP_MINIO_URL=http://localhost:9000
export REACT_APP_MINIO_BUCKET=cinema-files

# Запуск
yarn start
```

## Переменные окружения

| Переменная               | Значение по умолчанию   | Описание           |
| ------------------------ | ----------------------- | ------------------ |
| `REACT_APP_API_URL`      | `http://localhost:8001` | URL Main Service   |
| `REACT_APP_AUTH_URL`     | `http://localhost:8000` | URL Auth Service   |
| `REACT_APP_MINIO_URL`    | `http://localhost:9000` | URL MinIO          |
| `REACT_APP_MINIO_BUCKET` | `cinema-files`          | Имя bucket в MinIO |

## Функциональность

### ✅ Работает

- Аутентификация (логин/логаут)
- Просмотр списка фильмов
- Просмотр деталей фильма
- Поиск фильмов (базовый)
- Отображение постеров через прокси

### ⚠️ Частично работает

- Поиск (простой поиск по названию на клиенте)
- Рекомендации (возвращает топ фильмы)
- Похожие фильмы (случайные фильмы)

### ❌ Не реализовано в новом бекенде

- Добавление фильмов через админ панель
- Elasticsearch поиск
- Система рекомендаций
- Жанры фильмов
- Избранное и списки просмотра

## Структура данных

### Старый формат (Film)

```typescript
interface Film {
  movie_id: number
  title: string
  description: string
  release_date: string
  rating: number
  poster_url: string | null
  video_url: string
  duration: number
  genres: string[]
}
```

### Новый формат (BackendMovie)

```typescript
interface BackendMovie {
  id: number
  title: string
  description: string
  release_date: string
  rating: number
  poster_url: string | null
  movie_url: string
  duration: number
  created_at: string
  updated_at: string
}
```

## API Endpoints

### Auth Service (port 8000)

- `POST /auth/login` - вход в систему
- `POST /auth/register` - регистрация
- `POST /auth/logout` - выход
- `GET /auth/me` - информация о пользователе

### Main Service (port 8001)

- `GET /movies` - список фильмов
- `GET /movies/{id}` - фильм по ID
- `GET /proxy/poster/{movie_id}` - прокси для постеров
- `POST /files/upload` - загрузка файлов

## Отладка

### Проверка подключения к бекенду

```bash
# Проверка Auth Service
curl http://localhost:8000/

# Проверка Main Service
curl http://localhost:8001/

# Проверка MinIO
curl http://localhost:9000/minio/health/live
```

### Логи

Все API запросы логируются в консоль браузера с префиксами:

- `✨ API Response` - успешные ответы
- `🔥 API Error` - ошибки

## Известные проблемы

1. **TypeScript ошибки** - требуется установка `@types/node` и `@types/react`
2. **CORS** - постеры загружаются через прокси для избежания CORS
3. **Поиск** - пока реализован только базовый поиск на клиенте
4. **Жанры** - не реализованы в новом бекенде

## Планы развития

1. Реализация полноценного поиска на бекенде
2. Добавление системы жанров
3. Реализация рекомендаций
4. Добавление админ панели для управления фильмами
5. Интеграция с Elasticsearch

## Поддержка

При возникновении проблем:

1. Проверьте, что все сервисы бекенда запущены
2. Убедитесь, что переменные окружения установлены правильно
3. Проверьте логи в консоли браузера
4. Убедитесь, что MinIO содержит данные о фильмах
