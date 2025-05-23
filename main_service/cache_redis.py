from redis.asyncio import Redis
from auth_service.config import get_redis_settings

REDIS_SETTINGS = get_redis_settings()

redis_client = Redis(
    host=REDIS_SETTINGS["host"],
    port=REDIS_SETTINGS["port"],
    decode_responses=True
)