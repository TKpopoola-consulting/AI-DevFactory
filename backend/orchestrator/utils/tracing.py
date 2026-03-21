# backend/orchestrator/utils/tracing.py
"""
OpenTelemetry distributed tracing
"""
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import os


def setup_tracing(app, service_name: str = "orchestrator"):
    """Setup OpenTelemetry tracing"""
    
    # Create resource
    resource = Resource(attributes={
        SERVICE_NAME: service_name,
        "service.version": "2.0.0",
        "deployment.environment": os.getenv("ENVIRONMENT", "development")
    })
    
    # Set up tracer provider
    provider = TracerProvider(resource=resource)
    
    # Configure exporter
    otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    
    # Add span processor
    provider.add_span_processor(BatchSpanProcessor(exporter))
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument HTTP client
    HTTPXClientInstrumentor().instrument()
    
    return trace.get_tracer(__name__)


def create_span(name: str, attributes: dict = None):
    """Decorator to create spans"""
    tracer = trace.get_tracer(__name__)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name, attributes=attributes) as span:
                # Add attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator
