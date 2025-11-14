"""Backwards compatibility wrapper for the auth client."""

from .infraestructure.auth_client import verify_token  # noqa: F401

__all__ = ["verify_token"]
