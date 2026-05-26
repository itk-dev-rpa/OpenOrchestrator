"""Typed exceptions raised by the database access layer.

All "not found" errors inherit from both `OrchestratorError` and
`ValueError` so callers using the historical `except ValueError`
contract continue to work.
"""


class OrchestratorError(Exception):
    """Base class for all OpenOrchestrator domain errors."""


class TriggerNotFoundError(OrchestratorError, ValueError):
    """Raised when a trigger lookup by id returns nothing."""


class JobNotFoundError(OrchestratorError, ValueError):
    """Raised when a job lookup by id returns nothing."""


class ConstantNotFoundError(OrchestratorError, ValueError):
    """Raised when a constant lookup by name returns nothing."""


class CredentialNotFoundError(OrchestratorError, ValueError):
    """Raised when a credential lookup by name returns nothing."""


class QueueElementNotFoundError(OrchestratorError, ValueError):
    """Raised when a queue element lookup by id returns nothing."""
