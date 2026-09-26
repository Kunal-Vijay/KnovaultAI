import logging
import sys

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from prometheus_client import generate_latest, CollectorRegistry, Gauge
from pythonjsonlogger import jsonlogger

from app.core.config import settings

# --- Structured Logging Setup ---
def configure_structured_logging():
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(lineno)s %(pathname)s %(funcName)s"
    )
    log_handler.setFormatter(formatter)
    
    # Clear existing handlers to prevent duplicate logs
    logging.getLogger().handlers.clear()
    
    logging.basicConfig(level=logging.INFO, handlers=[log_handler])
    
    # Instrument Python's logging to emit traces
    LoggingInstrumentor().instrument(set_logging_format=True)
    
    logging.getLogger("uvicorn").handlers.clear()
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn").addHandler(log_handler)
    logging.getLogger("uvicorn.access").addHandler(log_handler)


# --- OpenTelemetry Tracing Setup ---
OTEL_RESOURCE_ATTRIBUTES = {
    "service.name": settings.OTEL_SERVICE_NAME,
    "service.version": settings.PROJECT_VERSION,
    "environment": "development", # or staging/production
}

def configure_opentelemetry_tracing(app):
    log = logging.getLogger(__name__)
    if not settings.OTEL_TRACES_ENABLED:
        log.info("OpenTelemetry tracing disabled (OTEL_TRACES_ENABLED=false).")
        return

    endpoint = (settings.OTEL_EXPORTER_OTLP_ENDPOINT or "").strip()
    if not endpoint or endpoint.lower() in {"none", "false", "disabled", "off"}:
        log.info("OpenTelemetry OTLP export disabled (no collector endpoint).")
        return

    resource = Resource.create(OTEL_RESOURCE_ATTRIBUTES)

    otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
    # Batch export avoids blocking HTTP responses on collector outages (SimpleSpanProcessor retries sync).
    span_processor = BatchSpanProcessor(otlp_exporter)

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider, excluded_urls="/metrics,/health,/ready")


# --- Prometheus Metrics Setup ---
registry = CollectorRegistry()
active_requests_gauge = Gauge(
    'fastapi_active_requests', 
    'Number of active requests',
    registry=registry
)

def setup_prometheus_metrics(app):
    # Middleware for basic active request count
    @app.middleware("http")
    async def track_requests(request, call_next):
        active_requests_gauge.inc()
        response = await call_next(request)
        active_requests_gauge.dec()
        return response

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        return generate_latest().decode("utf-8")

# Global tracer instance
tracer = trace.get_tracer(__name__)

