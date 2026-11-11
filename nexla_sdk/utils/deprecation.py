"""Deprecation helpers for resource methods."""

import functools
import warnings
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def warn_deprecated(old: str, new: str) -> None:
    """Warn that `old` is replaced by `new`. Call it from the deprecated function."""
    warnings.warn(
        f"{old} is deprecated; use {new} instead.", DeprecationWarning, stacklevel=3
    )


def missing_route(method: str, route: str) -> Callable[[F], F]:
    """Mark a method whose backend route does not exist.

    The method keeps sending its request, so existing callers behave as before.
    Each call emits a DeprecationWarning.
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"{fn.__qualname__} calls {method} {route}, which does not exist "
                "on the Nexla API.",
                DeprecationWarning,
                stacklevel=2,
            )
            return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
