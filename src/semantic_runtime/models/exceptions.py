"""Exceptions for semantic model validation."""


class ModelError(Exception):
    """Base error for semantic model problems."""


class ModelValidationError(ModelError):
    """Raised when a semantic model fails validation."""

    def __init__(self, model: str, field: str, message: str) -> None:
        self.model = model
        self.field = field
        self.message = message
        super().__init__(f"{model}.{field}: {message}")
