from log_service.cache_redis import redis_client
from elasticsearch import AsyncElasticsearch
from log_service.config import get_elasticsearch_settings
import json
import asyncio
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisListener:
    def __init__(self):
        self.running = False
        self.pubsub = None
        self.es_settings = get_elasticsearch_settings()
        self.es_client = None

    async def initialize_elasticsearch(self):
        """Initialize Elasticsearch client"""
        try:
            self.es_client = AsyncElasticsearch(
                hosts=[f"http://{self.es_settings['host']}:{self.es_settings['port']}"],
                basic_auth=(self.es_settings['username'], self.es_settings['password']),
                verify_certs=False
            )
            # Test connection
            await self.es_client.info()
            logger.info("Successfully connected to Elasticsearch")
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch: {e}")
            raise

    async def start_listening(self):
        """Start listening to Redis pub/sub events"""
        try:
            await self.initialize_elasticsearch()
            self.running = True
            self.pubsub = redis_client.pubsub()
            await self.pubsub.subscribe('logs')
            logger.info("Started listening to Redis pub/sub events")
            
            while self.running:
                try:
                    message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                    if message:
                        await self.process_message(message)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in start_listening: {e}")
            raise

    async def stop_listening(self):
        """Stop listening to Redis pub/sub events"""
        self.running = False
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        if self.es_client:
            await self.es_client.close()
        logger.info("Stopped listening to Redis pub/sub events")

    async def process_message(self, message):
        """Process received message and store in Elasticsearch"""
        try:
            data = json.loads(message['data'])
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'service': data.get('service', 'unknown'),
                'level': data.get('level', 'info'),
                'message': data.get('message', ''),
                'metadata': data.get('metadata', {})
            }
            
            await self.es_client.index(
                index='logs',
                document=log_entry
            )
            logger.info(f"Successfully stored log entry: {log_entry}")
        except Exception as e:
            logger.error(f"Error storing log in Elasticsearch: {e}")

redis_listener = RedisListener() 