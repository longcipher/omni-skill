"""Search engine integration module.

Provides a unified SearchEngine that combines Indexer and BM25Searcher
for end-to-end indexing and search functionality.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import structlog

from omniskill.core.indexer import Indexer
from omniskill.core.search import BM25Searcher

if TYPE_CHECKING:
    from omniskill.models import SearchResult

if TYPE_CHECKING:
    from omniskill.models import Chunk, Document

logger = structlog.get_logger()


class SearchEngine:
    """Unified search engine combining indexing and search.

    Provides a complete pipeline from file indexing to search,
    with optional filtering by document type and tags.

    Attributes:
        indexer: The document indexer.
        searcher: The BM25 searcher.
    """

    def __init__(
        self,
        indexer: Indexer | None = None,
        searcher: BM25Searcher | None = None,
    ) -> None:
        """Initialize the search engine.

        Args:
            indexer: Optional indexer instance. Creates a new one if not provided.
            searcher: Optional searcher instance. Creates a new one if not provided.
        """
        self.indexer = indexer or Indexer()
        self.searcher = searcher or BM25Searcher()

    def index_directory(self, directory: str | Path) -> list[Document | Chunk]:
        """Index all supported files in a directory.

        Args:
            directory: Path to the directory to index.

        Returns:
            A list of indexed Document and Chunk objects.

        Raises:
            ValueError: If the directory does not exist.
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            msg = f"Directory does not exist: {directory}"
            raise ValueError(msg)

        if not dir_path.is_dir():
            msg = f"Path is not a directory: {directory}"
            raise ValueError(msg)

        logger.info("indexing_directory", directory=str(dir_path))

        documents = self.indexer.index_directory(str(dir_path))
        self.searcher.add_documents(documents)

        logger.info(
            "indexing_complete",
            directory=str(dir_path),
            document_count=len(documents),
        )

        return documents

    def index_file(self, file_path: str | Path) -> list[Document | Chunk]:
        """Index a single file.

        Args:
            file_path: Path to the file to index.

        Returns:
            A list of indexed Document or Chunk objects.

        Raises:
            ValueError: If the file does not exist or is unsupported.
        """
        path = Path(file_path)
        if not path.exists():
            msg = f"File does not exist: {file_path}"
            raise ValueError(msg)

        if not path.is_file():
            msg = f"Path is not a file: {file_path}"
            raise ValueError(msg)

        logger.info("indexing_file", file_path=str(path))

        documents = self.indexer.index_file(str(path))
        self.searcher.add_documents(documents)

        logger.info(
            "file_indexed",
            file_path=str(path),
            document_count=len(documents),
        )

        return documents

    def search(
        self,
        query: str,
        limit: int = 10,
        doc_type: str | None = None,
        tags: list[str] | None = None,
    ) -> list[SearchResult]:
        """Search indexed documents.

        Args:
            query: The search query.
            limit: Maximum number of results to return.
            doc_type: Filter by document type ('csv' or 'markdown').
            tags: Filter by tags (all tags must match - AND logic).

        Returns:
            A list of SearchResult objects ordered by relevance score.

        Raises:
            ValueError: If the query is empty.
            ValueError: If no documents are indexed.
        """
        logger.info(
            "searching",
            query=query,
            limit=limit,
            doc_type=doc_type,
            tags=tags,
        )

        results = self.searcher.search(
            query=query,
            limit=limit,
            doc_type=doc_type,
            tags=tags,
        )

        logger.info(
            "search_complete",
            query=query,
            result_count=len(results),
        )

        return results

    def clear(self) -> None:
        """Clear all indexed documents."""
        self.searcher = BM25Searcher()
        logger.info("index_cleared")
