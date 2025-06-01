#!/bin/bash

# Скрипт для запуска фронтенда с настройками для нового бекенда

echo "🚀 Запуск фронтенда с настройками для нового бекенда..."

# Устанавливаем переменные окружения
export REACT_APP_API_URL=http://localhost:8001
export REACT_APP_AUTH_URL=http://localhost:8000
export REACT_APP_MINIO_URL=http://localhost:9000
export REACT_APP_MINIO_BUCKET=cinema-files
export REACT_APP_ENV=development

echo "📋 Настройки:"
echo "  API URL: $REACT_APP_API_URL"
echo "  Auth URL: $REACT_APP_AUTH_URL"
echo "  MinIO URL: $REACT_APP_MINIO_URL"
echo "  MinIO Bucket: $REACT_APP_MINIO_BUCKET"

# Проверяем, установлены ли зависимости
if [ ! -d "node_modules" ]; then
    echo "📦 Устанавливаем зависимости..."
    yarn install
fi

echo "🌐 Запускаем фронтенд..."
yarn start 