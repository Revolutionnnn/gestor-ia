"""Backwards compatibility stubs for migrated dependency helpers."""

from .services.auth_dependencies import (  # noqa: F401
    get_admin_user,
    get_current_user,
    get_optional_user,
    get_product_or_404,
)

__all__ = [
    "get_admin_user",
    "get_current_user",
    "get_optional_user",
    "get_product_or_404",
]
