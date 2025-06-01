#!/usr/bin/env python3
"""
Скрипт для полной очистки S3 хранилища (автоматический)
"""

import asyncio
from aiobotocore.session import get_session

# Настройки S3 (используем локальный MinIO)
S3_CONFIG = {
    "endpoint_url": "http://localhost:9000",
    "region_name": "us-east-1",
    "aws_access_key_id": "minioadmin",
    "aws_secret_access_key": "minioadmin123"
}

bucket_name = "cinema-files"


async def clear_s3_bucket():
    """Удаляет все объекты из S3 bucket"""
    session = get_session()
    async with session.create_client("s3", **S3_CONFIG) as s3:
        try:
            print(f"🗑️ Начинаем очистку bucket: {bucket_name}")
            
            # Получаем список всех объектов
            response = await s3.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' not in response:
                print("✅ Bucket уже пустой")
                return
            
            objects = response['Contents']
            total_objects = len(objects)
            total_size = sum(obj['Size'] for obj in objects)
            
            print(f"📊 Найдено объектов для удаления: {total_objects}")
            print(f"📊 Общий размер: {total_size / (1024*1024):.2f} MB")
            
            # Автоматическое подтверждение
            print(f"\n🚀 Автоматически удаляем все {total_objects} объектов...")
            
            # Удаляем объекты батчами (максимум 1000 за раз)
            deleted_count = 0
            batch_size = 1000
            
            for i in range(0, total_objects, batch_size):
                batch = objects[i:i + batch_size]
                
                # Формируем список для удаления
                delete_objects = {
                    'Objects': [{'Key': obj['Key']} for obj in batch]
                }
                
                # Удаляем батч
                delete_response = await s3.delete_objects(
                    Bucket=bucket_name,
                    Delete=delete_objects
                )
                
                batch_deleted = len(delete_response.get('Deleted', []))
                deleted_count += batch_deleted
                
                print(f"🗑️ Удалено: {deleted_count}/{total_objects} объектов")
                
                # Проверяем ошибки
                if 'Errors' in delete_response:
                    for error in delete_response['Errors']:
                        print(f"❌ Ошибка удаления {error['Key']}: {error['Message']}")
            
            print(f"\n✅ Очистка завершена!")
            print(f"📊 Удалено объектов: {deleted_count}")
            print(f"📊 Освобождено места: {total_size / (1024*1024):.2f} MB")
            
        except Exception as e:
            print(f"❌ Ошибка при очистке bucket: {e}")


async def verify_empty():
    """Проверяет что bucket действительно пустой"""
    session = get_session()
    async with session.create_client("s3", **S3_CONFIG) as s3:
        try:
            response = await s3.list_objects_v2(Bucket=bucket_name)
            
            if 'Contents' not in response:
                print("✅ Bucket пустой - очистка прошла успешно")
            else:
                remaining = len(response['Contents'])
                print(f"⚠️ В bucket осталось {remaining} объектов")
                
        except Exception as e:
            print(f"❌ Ошибка при проверке bucket: {e}")


async def main():
    """Основная функция"""
    print("🗑️ Автоматическая очистка S3 хранилища")
    print("=" * 50)
    
    await clear_s3_bucket()
    await verify_empty()
    
    print(f"\n🌐 MinIO Console: http://localhost:9001")
    print(f"🌐 MinIO API: http://localhost:9000")
    print(f"🔑 Логин: minioadmin / minioadmin123")


if __name__ == "__main__":
    asyncio.run(main()) 