"""Custom exceptions for ADO client operations."""


class AdoClientError(Exception):
    """Base exception for ADO client errors."""
    pass


class AdoAuthError(AdoClientError):
    """Authentication error (401 Unauthorized)."""
    pass


class AdoNotFoundError(AdoClientError):
    """Resource not found (404)."""
    pass


class AdoConfigError(AdoClientError):
    """Configuration error (missing PAT, org, project, etc.)."""
    pass
