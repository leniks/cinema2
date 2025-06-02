import asyncio
import io
import logging
from typing import Optional, BinaryIO
from minio import Minio
from minio.error import S3Error
from PIL import Image
import requests

from main_service.config import get_minio_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.minio_settings = get_minio_settings()
        self.client = Minio(
            self.minio_settings["endpoint"],
            access_key=self.minio_settings["access_key"],
            secret_key=self.minio_settings["secret_key"],
            secure=False  # Для локального использования
        )
        self.bucket_name = self.minio_settings["bucket"]
        
    async def ensure_bucket_exists(self):
        """Создает bucket если он не существует"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Bucket {self.bucket_name} created")
            else:
                logger.info(f"Bucket {self.bucket_name} already exists")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise

    async def upload_file(self, file_path: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
        """Загружает файл в MinIO"""
        try:
            await self.ensure_bucket_exists()
            
            file_stream = io.BytesIO(file_data)
            
            # Загружаем файл
            self.client.put_object(
                self.bucket_name,
                file_path,
                file_stream,
                length=len(file_data),
                content_type=content_type
            )
            
            # Возвращаем URL для доступа к файлу
            file_url = f"http://localhost:9000/{self.bucket_name}/{file_path}"
            logger.info(f"File uploaded successfully: {file_url}")
            return file_url
            
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise

    async def download_file(self, file_path: str) -> Optional[bytes]:
        """Скачивает файл из MinIO"""
        try:
            response = self.client.get_object(self.bucket_name, file_path)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            return None

    async def delete_file(self, file_path: str) -> bool:
        """Удаляет файл из MinIO"""
        try:
            self.client.remove_object(self.bucket_name, file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            return False

    async def upload_image_from_url(self, image_url: str, file_path: str) -> str:
        """Скачивает изображение по URL и загружает в MinIO"""
        try:
            # Скачиваем изображение
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Проверяем, что это изображение
            image = Image.open(io.BytesIO(response.content))
            
            # Конвертируем в JPEG если нужно
            if image.format != 'JPEG':
                output = io.BytesIO()
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                image.save(output, format='JPEG', quality=85)
                image_data = output.getvalue()
            else:
                image_data = response.content
            
            # Загружаем в MinIO
            return await self.upload_file(file_path, image_data, "image/jpeg")
            
        except Exception as e:
            logger.error(f"Error uploading image from URL: {e}")
            raise

    async def get_file_url(self, file_path: str) -> str:
        """Возвращает URL для доступа к файлу"""
        return f"http://localhost:9000/{self.bucket_name}/{file_path}"

    def list_files(self, prefix: str = "") -> list:
        """Возвращает список файлов в bucket"""
        try:
            objects = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing files: {e}")
            return []

file_service = FileService() 