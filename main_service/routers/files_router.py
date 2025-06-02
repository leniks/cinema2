from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
import io
import logging

from main_service.services.file_service import file_service
from main_service.models.User import User
from main_service.services.dependencies_service import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/files', tags=['Работа с файлами'])

@router.post("/upload", summary="Загрузить файл")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "uploads",
    user_data: User = Depends(get_current_user)
):
    """Загружает файл в MinIO"""
    try:
        # Читаем содержимое файла
        file_content = await file.read()
        file_path = f"{folder}/{file.filename}"
        
        # Загружаем файл
        file_url = await file_service.upload_file(
            file_path, 
            file_content, 
            file.content_type or "application/octet-stream"
        )
        
        return {
            "message": "Файл успешно загружен",
            "file_url": file_url,
            "file_path": file_path,
            "filename": file.filename,
            "content_type": file.content_type
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")

@router.post("/upload-image-from-url", summary="Загрузить изображение по URL")
async def upload_image_from_url(
    image_url: str,
    filename: str,
    folder: str = "images",
    user_data: User = Depends(get_current_user)
):
    """Скачивает изображение по URL и загружает в MinIO"""
    try:

        file_path = f"{folder}/{filename}"
        
        # Загружаем изображение
        file_url = await file_service.upload_image_from_url(image_url, file_path)
        
        return {
            "message": "Изображение успешно загружено",
            "file_url": file_url,
            "file_path": file_path,
            "original_url": image_url
        }
        
    except Exception as e:
        logger.error(f"Error uploading image from URL: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки изображения: {str(e)}")

@router.get("/download/{file_path:path}", summary="Скачать файл")
async def download_file(file_path: str):
    """Скачивает файл из MinIO"""
    try:
        file_data = await file_service.download_file(file_path)
        
        if file_data is None:
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        # Определяем тип контента по расширению файла
        content_type = "application/octet-stream"
        if file_path.lower().endswith(('.jpg', '.jpeg')):
            content_type = "image/jpeg"
        elif file_path.lower().endswith('.png'):
            content_type = "image/png"
        elif file_path.lower().endswith('.gif'):
            content_type = "image/gif"
        elif file_path.lower().endswith('.mp4'):
            content_type = "video/mp4"
        elif file_path.lower().endswith('.json'):
            content_type = "application/json"
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={file_path.split('/')[-1]}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка скачивания файла: {str(e)}")

@router.delete("/delete/{file_path:path}", summary="Удалить файл")
async def delete_file(
    file_path: str,
    user_data: User = Depends(get_current_user)
):
    """Удаляет файл из MinIO"""
    try:
        success = await file_service.delete_file(file_path)
        
        if not success:
            raise HTTPException(status_code=404, detail="Файл не найден или не удалось удалить")
        
        return {"message": "Файл успешно удален", "file_path": file_path}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления файла: {str(e)}")

@router.get("/list", summary="Получить список файлов")
async def list_files(
    prefix: str = "",
    user_data: User = Depends(get_current_user)
):
    """Возвращает список файлов в bucket"""
    try:
        files = file_service.list_files(prefix)
        
        return {
            "files": files,
            "count": len(files),
            "prefix": prefix
        }
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка файлов: {str(e)}")

@router.get("/url/{file_path:path}", summary="Получить URL файла")
async def get_file_url(file_path: str):
    """Возвращает URL для доступа к файлу"""
    try:
        file_url = await file_service.get_file_url(file_path)
        
        return {
            "file_url": file_url,
            "file_path": file_path
        }
        
    except Exception as e:
        logger.error(f"Error getting file URL: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения URL файла: {str(e)}") 