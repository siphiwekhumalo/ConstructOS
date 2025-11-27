"""
OpenTelemetry Configuration for ConstructOS

Provides distributed tracing and observability for the platform,
enabling cross-service monitoring and performance analysis.
"""

import os
from functools import wraps
from typing import Any, Callable, Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode


OTEL_ENABLED = os.getenv('OTEL_ENABLED', 'false').lower() == 'true'
OTEL_SERVICE_NAME = os.getenv('OTEL_SERVICE_NAME', 'constructos-backend')
OTEL_EXPORTER_ENDPOINT = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', '')
OTEL_ENVIRONMENT = os.getenv('OTEL_ENVIRONMENT', 'development')


def setup_telemetry():
    """
    Initialize OpenTelemetry tracing with appropriate exporters.
    
    This should be called once during Django startup (e.g., in settings.py or wsgi.py).
    """
    if not OTEL_ENABLED:
        return
    
    resource = Resource.create({
        'service.name': OTEL_SERVICE_NAME,
        'service.version': os.getenv('APP_VERSION', '1.0.0'),
        'deployment.environment': OTEL_ENVIRONMENT,
        'service.namespace': 'constructos',
    })
    
    provider = TracerProvider(resource=resource)
    
    if OTEL_EXPORTER_ENDPOINT:
        otlp_exporter = OTLPSpanExporter(
            endpoint=OTEL_EXPORTER_ENDPOINT,
            insecure=OTEL_ENVIRONMENT == 'development'
        )
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    if OTEL_ENVIRONMENT == 'development' and os.getenv('OTEL_CONSOLE_EXPORT', 'false').lower() == 'true':
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    trace.set_tracer_provider(provider)
    
    DjangoInstrumentor().instrument()
    RequestsInstrumentor().instrument()


def get_tracer(name: str = None) -> trace.Tracer:
    """
    Get a tracer instance for creating spans.
    
    Args:
        name: Optional name for the tracer (defaults to service name)
    
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name or OTEL_SERVICE_NAME)


def traced(
    name: Optional[str] = None,
    attributes: Optional[dict] = None,
    record_exception: bool = True
):
    """
    Decorator to automatically create a span for a function.
    
    Args:
        name: Optional span name (defaults to function name)
        attributes: Optional static attributes to add to the span
        record_exception: Whether to record exceptions in the span
    
    Usage:
        @traced(name="process_document", attributes={"component": "document_processor"})
        def process_document(doc_id):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not OTEL_ENABLED:
                return func(*args, **kwargs)
            
            tracer = get_tracer()
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    if record_exception:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        
        return wrapper
    return decorator


class SpanContext:
    """
    Context manager for creating spans with automatic error handling.
    
    Usage:
        with SpanContext("process_order", {"order_id": order.id}) as span:
            # Process order
            span.add_event("validation_complete")
            # More processing
    """
    
    def __init__(
        self,
        name: str,
        attributes: Optional[dict] = None,
        record_exception: bool = True
    ):
        self.name = name
        self.attributes = attributes or {}
        self.record_exception = record_exception
        self.span = None
    
    def __enter__(self) -> 'SpanContextWrapper':
        if not OTEL_ENABLED:
            return SpanContextWrapper(None)
        
        tracer = get_tracer()
        self.span = tracer.start_span(self.name)
        
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
        
        return SpanContextWrapper(self.span)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.span:
            return False
        
        if exc_type is not None and self.record_exception:
            self.span.record_exception(exc_val)
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self.span.set_status(Status(StatusCode.OK))
        
        self.span.end()
        return False


class SpanContextWrapper:
    """Wrapper to provide span-like interface even when tracing is disabled."""
    
    def __init__(self, span: Optional[trace.Span]):
        self._span = span
    
    def set_attribute(self, key: str, value: Any):
        """Set an attribute on the span."""
        if self._span:
            self._span.set_attribute(key, value)
    
    def add_event(self, name: str, attributes: Optional[dict] = None):
        """Add an event to the span."""
        if self._span:
            self._span.add_event(name, attributes or {})
    
    def record_exception(self, exception: Exception):
        """Record an exception on the span."""
        if self._span:
            self._span.record_exception(exception)
    
    def set_status(self, status: Status):
        """Set the status of the span."""
        if self._span:
            self._span.set_status(status)


def add_span_attribute(key: str, value: Any):
    """
    Add an attribute to the current span.
    
    Args:
        key: Attribute key
        value: Attribute value
    """
    if not OTEL_ENABLED:
        return
    
    current_span = trace.get_current_span()
    if current_span:
        current_span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[dict] = None):
    """
    Add an event to the current span.
    
    Args:
        name: Event name
        attributes: Optional event attributes
    """
    if not OTEL_ENABLED:
        return
    
    current_span = trace.get_current_span()
    if current_span:
        current_span.add_event(name, attributes or {})


def record_span_exception(exception: Exception):
    """
    Record an exception on the current span.
    
    Args:
        exception: The exception to record
    """
    if not OTEL_ENABLED:
        return
    
    current_span = trace.get_current_span()
    if current_span:
        current_span.record_exception(exception)
        current_span.set_status(Status(StatusCode.ERROR, str(exception)))


SPAN_ATTRIBUTES = {
    'db': {
        'system': 'db.system',
        'name': 'db.name',
        'statement': 'db.statement',
        'operation': 'db.operation',
    },
    'http': {
        'method': 'http.method',
        'url': 'http.url',
        'status_code': 'http.status_code',
        'target': 'http.target',
    },
    'user': {
        'id': 'enduser.id',
        'role': 'enduser.role',
    },
    'business': {
        'project_id': 'constructos.project.id',
        'document_id': 'constructos.document.id',
        'account_id': 'constructos.account.id',
        'transaction_id': 'constructos.transaction.id',
    }
}
