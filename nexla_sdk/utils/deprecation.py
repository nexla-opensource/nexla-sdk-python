"""Deprecation helpers for resource methods."""

import functools
import warnings
from typing import Any, Callable, Optional, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def warn_deprecated(old: str, new: str) -> None:
    """Warn that `old` is replaced by `new`. Call it from the deprecated function."""
    warnings.warn(
        f"{old} is deprecated; use {new} instead.", DeprecationWarning, stacklevel=3
    )


def missing_route(
    method: str, route: str, use: Optional[str] = None
) -> Callable[[F], F]:
    """Mark a method whose backend route does not exist.

    The method keeps sending its request, so existing callers behave as before.
    Each call emits a DeprecationWarning. `use` names a working replacement.
    """

    def decorator(fn: F) -> F:
        hint = f" Use {use} instead." if use else ""

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"{fn.__qualname__} calls {method} {route}, which does not exist "
                f"on the Nexla API.{hint}",
                DeprecationWarning,
                stacklevel=2,
            )
            return fn(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
