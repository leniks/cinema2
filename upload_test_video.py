#!/usr/bin/env python3

import os
import subprocess
import tempfile
from minio import Minio
from minio.error import S3Error

def create_test_video():
    """Создание тестового видео с помощью ffmpeg"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    temp_file.close()
    
    cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=10:size=1280x720:rate=30',
        '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=10',
        '-c:v', 'libx264', '-c:a', 'aac', '-shortest', '-y', temp_file.name
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return temp_file.name
    except subprocess.CalledProcessError as e:
        print(f"Ошибка создания видео: {e}")
        return None
    except FileNotFoundError:
        print("ffmpeg не найден. Создаю простой файл-заглушку...")
        with open(temp_file.name, 'wb') as f:
            f.write(b'FAKE_VIDEO_FILE_FOR_TESTING' * 1000)
        return temp_file.name

def upload_to_minio():
    """Загрузка тестового видео в MinIO"""
    # Настройки MinIO
    client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin123",
        secure=False
    )
    
    bucket_name = "cinema-files"
    
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket {bucket_name} создан")
        
        video_file = create_test_video()
        if not video_file:
            return False
        
        object_name = "videos/test_movie.mp4"
        client.fput_object(bucket_name, object_name, video_file)
        print(f"Тестовое видео загружено: {object_name}")
        
        test_images = [
            ("posters/test_poster_1.jpg", "Test poster 1"),
            ("posters/test_poster_2.jpg", "Test poster 2"),
            ("backdrops/test_backdrop_1.jpg", "Test backdrop 1"),
            ("backdrops/test_backdrop_2.jpg", "Test backdrop 2"),
            ("actors/test_actor_1.jpg", "Test actor photo 1"),
            ("actors/test_actor_2.jpg", "Test actor photo 2"),
        ]
        
        for object_name, description in test_images:
            temp_img = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_img.write(f"FAKE_IMAGE_{description}".encode() * 100)
            temp_img.close()
            
            client.fput_object(bucket_name, object_name, temp_img.name)
            print(f"Загружено: {object_name}")
            os.unlink(temp_img.name)
        
        os.unlink(video_file)
        
        return True
        
    except S3Error as e:
        print(f"Ошибка MinIO: {e}")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("Загрузка тестовых файлов в MinIO...")
    if upload_to_minio():
        print("Тестовые файлы успешно загружены!")
    else:
        print("Ошибка загрузки файлов") 