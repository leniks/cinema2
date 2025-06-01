import os
import logging
from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor

logger = logging.getLogger(__name__)

class CinemaTracer:
    """Централизованная настройка трейсинга для всех сервисов Cinema"""
    
    def __init__(self, service_name: str, service_version: str = "1.0.0"):
        self.service_name = service_name
        self.service_version = service_version
        self.tracer: Optional[trace.Tracer] = None
        self._initialized = False
    
    def initialize(self) -> trace.Tracer:
        """Инициализация трейсинга для сервиса"""
        if self._initialized:
            return self.tracer
        
        try:
            # Настройка ресурса с метаданными сервиса
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": self.service_version,
                "service.namespace": "cinema",
                "deployment.environment": os.getenv("ENVIRONMENT", "development"),
            })
            
            # Создание TracerProvider
            trace.set_tracer_provider(TracerProvider(resource=resource))
            
            # Настройка экспортера в Jaeger через OTLP
            jaeger_endpoint = os.getenv("JAEGER_OTLP_ENDPOINT", "http://jaeger:4317")
            otlp_exporter = OTLPSpanExporter(
                endpoint=jaeger_endpoint,
                insecure=True  # Для development
            )
            
            # Добавление процессора для экспорта спанов
            span_processor = BatchSpanProcessor(otlp_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            # Создание трейсера
            self.tracer = trace.get_tracer(
                instrumenting_module_name=self.service_name,
                instrumenting_library_version=self.service_version
            )
            
            self._initialized = True
            logger.info(f"Трейсинг инициализирован для сервиса: {self.service_name}")
            
            return self.tracer
            
        except Exception as e:
            logger.error(f"Ошибка инициализации трейсинга: {e}")
            # Возвращаем NoOp трейсер если не удалось настроить
            return trace.NoOpTracer()
    
    def instrument_fastapi(self, app):
        """Автоматическое инструментирование FastAPI приложения"""
        try:
            FastAPIInstrumentor.instrument_app(
                app,
                tracer_provider=trace.get_tracer_provider(),
                excluded_urls="health,metrics"  # Исключаем служебные endpoints
            )
            logger.info("FastAPI инструментирован для трейсинга")
        except Exception as e:
            logger.error(f"Ошибка инструментирования FastAPI: {e}")
    
    def instrument_requests(self):
        """Автоматическое инструментирование HTTP requests"""
        try:
            RequestsInstrumentor().instrument()
            logger.info("Requests инструментирован для трейсинга")
        except Exception as e:
            logger.error(f"Ошибка инструментирования Requests: {e}")
    
    def instrument_aiohttp(self):
        """Автоматическое инструментирование aiohttp client"""
        try:
            AioHttpClientInstrumentor().instrument()
            logger.info("AioHttp Client инструментирован для трейсинга")
        except Exception as e:
            logger.error(f"Ошибка инструментирования AioHttp: {e}")
    
    def instrument_sqlalchemy(self, engine=None):
        """Автоматическое инструментирование SQLAlchemy"""
        try:
            if engine:
                SQLAlchemyInstrumentor().instrument(engine=engine)
            else:
                SQLAlchemyInstrumentor().instrument()
            logger.info("SQLAlchemy инструментирован для трейсинга")
        except Exception as e:
            logger.error(f"Ошибка инструментирования SQLAlchemy: {e}")
    
    def instrument_redis(self):
        """Автоматическое инструментирование Redis"""
        try:
            RedisInstrumentor().instrument()
            logger.info("Redis инструментирован для трейсинга")
        except Exception as e:
            logger.error(f"Ошибка инструментирования Redis: {e}")
    
    def instrument_elasticsearch(self):
        """Автоматическое инструментирование Elasticsearch"""
        try:
            ElasticsearchInstrumentor().instrument()
            logger.info("Elasticsearch инструментирован для трейсинга")
        except Exception as e:
            logger.error(f"Ошибка инструментирования Elasticsearch: {e}")
    
    def instrument_all(self, app=None, sqlalchemy_engine=None):
        """Инструментирование всех поддерживаемых библиотек"""
        self.instrument_requests()
        self.instrument_aiohttp()
        self.instrument_redis()
        self.instrument_elasticsearch()
        
        if sqlalchemy_engine:
            self.instrument_sqlalchemy(sqlalchemy_engine)
        
        if app:
            self.instrument_fastapi(app)
    
    def create_span(self, name: str, **kwargs):
        """Создание кастомного спана"""
        if self.tracer:
            return self.tracer.start_span(name, **kwargs)
        return trace.NoOpTracer().start_span(name)
    
    def add_span_attributes(self, span, attributes: dict):
        """Добавление атрибутов к спану"""
        try:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        except Exception as e:
            logger.error(f"Ошибка добавления атрибутов к спану: {e}")
    
    def add_span_event(self, span, name: str, attributes: dict = None):
        """Добавление события к спану"""
        try:
            span.add_event(name, attributes or {})
        except Exception as e:
            logger.error(f"Ошибка добавления события к спану: {e}")

def get_tracer(service_name: str, service_version: str = "1.0.0") -> CinemaTracer:
    """Фабричная функция для создания трейсера"""
    return CinemaTracer(service_name, service_version)

def get_current_span():
    """Получение текущего активного спана"""
    return trace.get_current_span()

def get_trace_id() -> str:
    """Получение ID текущего трейса"""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, '032x')
    return ""

def get_span_id() -> str:
    """Получение ID текущего спана"""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, '016x')
    return "" 