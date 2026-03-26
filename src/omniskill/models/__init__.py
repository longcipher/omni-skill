"""Core data models for the OmniSkill framework.

This module defines the foundational data structures used throughout
the framework for documents, chunks, and search results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class Document:
    """Represents a document from CSV or Markdown files.

    Attributes:
        id: Unique identifier for the document.
        source: Source file path or identifier.
        content: The document content.
        metadata: Additional metadata as a dictionary.
        tags: Optional list of tags associated with the document.
    """

    id: str
    source: str
    content: str
    metadata: dict[str, Any] = field(hash=False)
    tags: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class Chunk:
    """Represents a sub-section (chunk) of a Markdown document.

    Attributes:
        id: Unique identifier for the chunk.
        source: Source file path or identifier of the parent document.
        content: The chunk content.
        header_level: The markdown header level (1-6) if the chunk starts with a header.
        header_text: The text of the header if present.
        tags: Optional list of tags inherited from parent document.
    """

    id: str
    source: str
    content: str
    header_level: int | None
    header_text: str | None
    tags: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class SearchResult:
    """Represents a search result with BM25 scoring.

    Attributes:
        document: The matched Document or Chunk.
        score: The BM25 relevance score (higher is better).
    """

    document: Document | Chunk
    score: float
