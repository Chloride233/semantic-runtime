"""Runtime error model aligned with the API & MCP specification."""

from __future__ import annotations


class SemanticRuntimeError(Exception):
    """Base error for runtime failures, carrying a stable error code."""

    code: str

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ModelNotLoadedError(SemanticRuntimeError):
    """Raised when a model has not been loaded into the runtime."""

    code = "MODEL_NOT_LOADED"


class EntityNotFoundError(SemanticRuntimeError):
    """Raised when an entity id is not present in the registry."""

    code = "ENTITY_NOT_FOUND"


class RelationNotFoundError(SemanticRuntimeError):
    """Raised when a relation id is not present in the registry."""

    code = "RELATION_NOT_FOUND"


class DuplicateModelError(SemanticRuntimeError):
    """Raised when a model is registered twice."""

    code = "DUPLICATE_MODEL"


class PolicyDeniedError(SemanticRuntimeError):
    """Raised when a policy denies an operation."""

    code = "POLICY_DENIED"


class UnsafeOperationError(SemanticRuntimeError):
    """Raised when an operation is deemed unsafe."""

    code = "UNSAFE_OPERATION"
