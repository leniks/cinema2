#!/usr/bin/env python3

from minio import Minio
from minio.error import S3Error
import json

# MinIO настройки
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"
MINIO_BUCKET = "cinema-files"

def setup_public_access():
    """Настройка публичного доступа к bucket"""
    try:
        # Подключаемся к MinIO
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        
        # Проверяем существование bucket
        if not client.bucket_exists(MINIO_BUCKET):
            print(f"Bucket {MINIO_BUCKET} не существует")
            return
        
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{MINIO_BUCKET}/*"]
                }
            ]
        }
        
        client.set_bucket_policy(MINIO_BUCKET, json.dumps(policy))
        print(f"Публичный доступ к bucket {MINIO_BUCKET} настроен")
        
        objects = list(client.list_objects(MINIO_BUCKET, recursive=True))
        print(f"Всего файлов в bucket: {len(objects)}")
        
        posters = [obj for obj in objects if obj.object_name.startswith('posters/')]
        backdrops = [obj for obj in objects if obj.object_name.startswith('backdrops/')]
        actors = [obj for obj in objects if obj.object_name.startswith('actors/')]
        videos = [obj for obj in objects if obj.object_name.startswith('videos/')]
        
        print(f"Постеры: {len(posters)}")
        print(f"Бекдропы: {len(backdrops)}")
        print(f"Фото актеров: {len(actors)}")
        print(f"Видео: {len(videos)}")
        
    except S3Error as e:
        print(f"Ошибка MinIO: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("🔧 Настройка публичного доступа к MinIO")
    print("=" * 40)
    setup_public_access() 