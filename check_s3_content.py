#!/usr/bin/env python3
"""
Скрипт для проверки содержимого S3 хранилища
"""

import asyncio
import json
from aiobotocore.session import get_session

# Настройки S3 (используем локальный MinIO)
S3_CONFIG = {
    "endpoint_url": "http://localhost:9000",
    "region_name": "us-east-1",
    "aws_access_key_id": "minioadmin",
    "aws_secret_access_key": "minioadmin123"
}

bucket_name = "cinema-files"


async def list_s3_objects():
    """Выводит список всех объектов в S3 bucket"""
    session = get_session()
    async with session.create_client("s3", **S3_CONFIG) as s3:
        try:
            # Получаем список всех объектов
            response = await s3.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' not in response:
                print("❌ Bucket пустой или не существует")
                return
            
            objects = response['Contents']
            total_size = sum(obj['Size'] for obj in objects)
            
            print(f"📊 Bucket: {bucket_name}")
            print(f"📊 Всего объектов: {len(objects)}")
            print(f"📊 Общий размер: {total_size / (1024*1024):.2f} MB")
            print("=" * 60)
            
            # Группируем по фильмам
            movies = {}
            for obj in objects:
                key = obj['Key']
                if key.startswith('movies/'):
                    parts = key.split('/')
                    if len(parts) >= 3:
                        movie_id = parts[1]
                        file_type = parts[2]
                        
                        if movie_id not in movies:
                            movies[movie_id] = {}
                        
                        movies[movie_id][file_type] = {
                            'size': obj['Size'],
                            'modified': obj['LastModified']
                        }
            
            print(f"🎬 Найдено фильмов: {len(movies)}")
            print("\n📝 Примеры содержимого:")
            
            # Показываем первые 10 фильмов
            for i, (movie_id, files) in enumerate(list(movies.items())[:10]):
                print(f"\n🎬 Movie ID: {movie_id}")
                for file_type, info in files.items():
                    print(f"  - {file_type}: {info['size']} bytes")
            
            if len(movies) > 10:
                print(f"\n... и еще {len(movies) - 10} фильмов")
            
        except Exception as e:
            print(f"❌ Ошибка при получении списка объектов: {e}")


async def get_sample_metadata():
    """Получает и показывает пример метаданных фильма"""
    session = get_session()
    async with session.create_client("s3", **S3_CONFIG) as s3:
        try:
            # Получаем метаданные первого фильма
            metadata_key = "movies/1/metadata.json"
            response = await s3.get_object(Bucket=bucket_name, Key=metadata_key)
            content = await response['Body'].read()
            metadata = json.loads(content.decode('utf-8'))
            
            print("\n📄 Пример метаданных (Movie ID: 1):")
            print("=" * 40)
            print(json.dumps(metadata, ensure_ascii=False, indent=2))
            
        except Exception as e:
            print(f"❌ Ошибка при получении метаданных: {e}")


async def get_sample_info():
    """Получает и показывает пример info файла"""
    session = get_session()
    async with session.create_client("s3", **S3_CONFIG) as s3:
        try:
            # Получаем info файл первого фильма
            info_key = "movies/1/info.txt"
            response = await s3.get_object(Bucket=bucket_name, Key=info_key)
            content = await response['Body'].read()
            info_text = content.decode('utf-8')
            
            print("\n📄 Пример info файла (Movie ID: 1):")
            print("=" * 40)
            print(info_text)
            
        except Exception as e:
            print(f"❌ Ошибка при получении info файла: {e}")


async def main():
    """Основная функция"""
    print("🔍 Проверка содержимого S3 хранилища")
    print("=" * 50)
    
    await list_s3_objects()
    await get_sample_metadata()
    await get_sample_info()
    
    print(f"\n🌐 MinIO Console: http://localhost:9001")
    print(f"🌐 MinIO API: http://localhost:9000")
    print(f"🔑 Логин: minioadmin / minioadmin123")


if __name__ == "__main__":
    asyncio.run(main()) 