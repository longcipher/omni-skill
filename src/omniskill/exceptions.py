"""Custom exceptions for OmniSkill framework.

Provides a hierarchy of exceptions for different error conditions
with meaningful error messages and context.
"""

from __future__ import annotations


class OmniSkillError(Exception):
    """Base exception for OmniSkill framework.

    All OmniSkill-specific exceptions inherit from this class.
    """

    def __init__(self, message: str, *, context: dict | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message.
            context: Optional dictionary with additional context.
        """
        super().__init__(message)
        self.context = context or {}


class ConfigurationError(OmniSkillError):
    """Raised when configuration is invalid or missing.

    Examples:
        - Missing required configuration values
        - Invalid configuration file format
        - Environment variable parsing errors
    """

    def __init__(self, message: str, *, config_path: str | None = None, **kwargs: object) -> None:
        """Initialize the exception.

        Args:
            message: Error message.
            config_path: Path to the configuration file if applicable.
            **kwargs: Additional context.
        """
        context = {"config_path": config_path, **kwargs}
        super().__init__(message, context=context)


class IndexingError(OmniSkillError):
    """Raised when document indexing fails.

    Examples:
        - CSV parsing errors
        - Markdown parsing errors
        - File read errors
        - Invalid file format
    """

    def __init__(self, message: str, *, file_path: str | None = None, **kwargs: object) -> None:
        """Initialize the exception.

        Args:
            message: Error message.
            file_path: Path to the file that caused the error.
            **kwargs: Additional context.
        """
        context = {"file_path": file_path, **kwargs}
        super().__init__(message, context=context)


class SearchError(OmniSkillError):
    """Raised when search operation fails.

    Examples:
        - Empty query
        - Empty index
        - BM25 scoring errors
        - Invalid search parameters
    """

    def __init__(self, message: str, *, query: str | None = None, **kwargs: object) -> None:
        """Initialize the exception.

        Args:
            message: Error message.
            query: The search query that caused the error.
            **kwargs: Additional context.
        """
        context = {"query": query, **kwargs}
        super().__init__(message, context=context)


class AssemblyError(OmniSkillError):
    """Raised when prompt assembly fails.

    Examples:
        - Invalid output format
        - Context length exceeded
        - Formatting errors
        - Invalid search results
    """

    def __init__(self, message: str, *, output_format: str | None = None, **kwargs: object) -> None:
        """Initialize the exception.

        Args:
            message: Error message.
            output_format: The output format that caused the error.
            **kwargs: Additional context.
        """
        context = {"output_format": output_format, **kwargs}
        super().__init__(message, context=context)


class FileError(OmniSkillError):
    """Raised when file operation fails.

    Examples:
        - File not found
        - Permission denied
        - File too large
        - Unsupported file type
    """

    def __init__(self, message: str, *, file_path: str | None = None, **kwargs: object) -> None:
        """Initialize the exception.

        Args:
            message: Error message.
            file_path: Path to the file that caused the error.
            **kwargs: Additional context.
        """
        context = {"file_path": file_path, **kwargs}
        super().__init__(message, context=context)
