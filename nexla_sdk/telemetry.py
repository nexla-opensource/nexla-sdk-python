"""
Centralized OpenTelemetry utilities for the Nexla SDK.

This module isolates optional OpenTelemetry usage so the SDK works
without any OpenTelemetry packages installed. If tracing is disabled
or OpenTelemetry isn't available, a no-op tracer is provided.
"""

import os
import threading
from typing import Any, Optional

# Guard against missing OpenTelemetry installation
try:  # pragma: no cover - optional dependency
    from opentelemetry import trace  # type: ignore

    _opentelemetry_available = True
except Exception:  # pragma: no cover
    trace = None  # type: ignore
    _opentelemetry_available = False


class _NoOpSpan:
    def __enter__(self) -> "_NoOpSpan":  # noqa: D401
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def set_attribute(self, key: str, value: Any) -> None:
        pass

    def set_status(self, status: Any) -> None:  # signature compatible
        pass

    def record_exception(self, exception: BaseException) -> None:
        pass

    def is_recording(self) -> bool:
        return False


class _NoOpTracer:
    def start_as_current_span(self, *args: Any, **kwargs: Any) -> _NoOpSpan:  # noqa: D401
        return _NoOpSpan()

    def start_span(self, *args: Any, **kwargs: Any) -> _NoOpSpan:  # noqa: D401
        return _NoOpSpan()


# Tracer cache
_tracer: Optional["trace.Tracer"] = None  # type: ignore[name-defined]
_tracer_lock = threading.Lock()


def get_tracer(trace_enabled: bool):
    """
    Return an OpenTelemetry tracer if available and enabled, otherwise a no-op tracer.
    """
    global _tracer

    if not trace_enabled or not _opentelemetry_available:
        return _NoOpTracer()

    if _tracer is None:
        # Double-checked locking to avoid races in concurrent initialization
        with _tracer_lock:
            if _tracer is None:
                # Using a stable instrumentation name for the SDK tracer
                try:
                    from importlib.metadata import version  # Python 3.8+

                    pkg_version = version("nexla-sdk")
                except Exception:  # pragma: no cover
                    pkg_version = "unknown"
                # Assign inside the lock
                local_tracer = trace.get_tracer("nexla.sdk", pkg_version)  # type: ignore[union-attr]
                globals()["_tracer"] = local_tracer
    return _tracer


def is_tracing_configured() -> bool:
    """
    Heuristically detect if OpenTelemetry tracing is configured globally.

    Returns True when a non-noop tracer provider is set or when common
    OTEL exporter-related environment variables are present.
    """
    if not _opentelemetry_available:
        return False

    try:
        provider = trace.get_tracer_provider()  # type: ignore[union-attr]
        # If provider is not the default NoOpTracerProvider, assume configured
        if getattr(trace, "NoOpTracerProvider", None) and not isinstance(
            provider,
            trace.NoOpTracerProvider,  # type: ignore[attr-defined]
        ):
            return True
    except Exception:  # pragma: no cover
        # If anything odd happens, fall back to env var detection
        pass

    otel_env_vars = [
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        "OTEL_EXPORTER_JAEGER_AGENT_HOST",
        "OTEL_EXPORTER_ZIPKIN_ENDPOINT",
        "OTEL_SERVICE_NAME",
    ]
    if any(os.environ.get(var) for var in otel_env_vars):
        return True

    return False
