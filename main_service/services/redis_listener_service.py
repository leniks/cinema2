import asyncio
from main_service.cache_redis import redis_client
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisListenerService:
    def __init__(self):
        self.pubsub = redis_client.pubsub()
        self.running = False
        logger.info("RedisListenerService инициализирован")

    async def start_listening(self):
        """Запускает прослушивание Redis каналов"""
        logger.info("Начинаем прослушивание Redis каналов")
        self.running = True
        await self.pubsub.subscribe("movie_cache_update")
        logger.info("Подписались на канал movie_cache_update")
        
        while self.running:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    logger.info(f"Получено сообщение: {message}")
                    await self.process_message(message)
            except Exception as e:
                logger.error(f"Ошибка при получении сообщения: {e}")
            await asyncio.sleep(0.1)

    async def process_message(self, message):
        """Обработка полученного сообщения"""
        try:
            if message["type"] == "message":
                data = message["data"]
                logger.info(f"Обработка сообщения: {data}")
                # Здесь можно добавить логику обработки сообщения
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")

    async def stop_listening(self):
        """Останавливает прослушивание"""
        logger.info("Останавливаем прослушивание Redis")
        self.running = False
        await self.pubsub.unsubscribe()
        await self.pubsub.close()
        logger.info("Прослушивание Redis остановлено")

глобальный экземпляр сервиса
redis_listener = RedisListenerService() 