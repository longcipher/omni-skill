"""Core indexer implementations for CSV and Markdown documents.

Provides indexers that parse CSV files (row-by-row) and Markdown files
(chunked by H2/H3 headers) into Document and Chunk objects.
"""

from __future__ import annotations

import csv
import re
import uuid
from pathlib import Path

from omniskill.models import Chunk, Document


class CsvIndexer:
    """Indexes CSV files row-by-row into Document objects.

    Each row becomes a Document with the CSV headers as metadata keys.
    """

    def _extract_tags_from_path(self, path: Path) -> tuple[str, ...]:
        """Extract tags from file path components.

        Only extracts tags from skill-related directories (skills/, datasets/).
        This avoids extracting tags from temporary or system directories.

        Args:
            path: Path to the file.

        Returns:
            A tuple of tags extracted from directory names.

        """
        tags: list[str] = []
        # Only extract tags from skill-related directories
        for parent in path.parents:
            if parent.name in ("skills", "datasets"):
                continue
            # Stop at the first skill-related directory
            if parent.name == "skills":
                break
            # Extract tag from immediate parent if it's a skill directory
            if parent.parent.name == "skills" and parent.name:
                tags.append(parent.name)
                break
        return tuple(tags)

    def index_file(self, path: str) -> list[Document]:
        """Index a CSV file and return a list of Documents.

        Args:
            path: Path to the CSV file.

        Returns:
            A list of Document objects, one per data row.

        """
        docs: list[Document] = []
        file_path = Path(path)
        tags = self._extract_tags_from_path(file_path)

        try:
            with file_path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    return docs

                for row in reader:
                    metadata = dict(row)
                    content = " ".join(str(v) for v in row.values())
                    doc = Document(
                        id=f"{file_path.stem}-{uuid.uuid4().hex[:8]}",
                        source=str(file_path),
                        content=content,
                        metadata=metadata,
                        tags=tags,
                    )
                    docs.append(doc)
        except csv.Error:
            pass

        return docs


_HEADER_RE = re.compile(r"^(#{2,3})\s+(.+)$", re.MULTILINE)


class MarkdownIndexer:
    """Indexes Markdown files by chunking at H2/H3 headers.

    Content before the first header is included as a single chunk if
    non-empty. Each header section becomes its own Chunk.
    """

    def _extract_tags_from_path(self, path: Path) -> tuple[str, ...]:
        """Extract tags from file path components.

        Only extracts tags from skill-related directories (skills/, datasets/).
        This avoids extracting tags from temporary or system directories.

        Args:
            path: Path to the file.

        Returns:
            A tuple of tags extracted from directory names.

        """
        tags: list[str] = []
        # Only extract tags from skill-related directories
        for parent in path.parents:
            if parent.name in ("skills", "datasets"):
                continue
            # Stop at the first skill-related directory
            if parent.name == "skills":
                break
            # Extract tag from immediate parent if it's a skill directory
            if parent.parent.name == "skills" and parent.name:
                tags.append(parent.name)
                break
        return tuple(tags)

    def index_file(self, path: str) -> list[Chunk]:
        """Index a Markdown file and return a list of Chunks.

        Args:
            path: Path to the Markdown file.

        Returns:
            A list of Chunk objects, one per header section.

        """
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        tags = self._extract_tags_from_path(file_path)

        if not text.strip():
            return []

        chunks: list[Chunk] = []
        matches = list(_HEADER_RE.finditer(text))

        if not matches:
            content = text.strip()
            if content:
                chunks.append(
                    Chunk(
                        id=f"{file_path.stem}-{uuid.uuid4().hex[:8]}",
                        source=str(file_path),
                        content=content,
                        header_level=None,
                        header_text=None,
                        tags=tags,
                    )
                )
            return chunks

        first_match_start = matches[0].start()
        preamble = text[:first_match_start].strip()
        if preamble:
            chunks.append(
                Chunk(
                    id=f"{file_path.stem}-{uuid.uuid4().hex[:8]}",
                    source=str(file_path),
                    content=preamble,
                    header_level=None,
                    header_text=None,
                    tags=tags,
                )
            )

        for i, match in enumerate(matches):
            level = len(match.group(1))
            header_text = match.group(2).strip()
            content_start = match.end()
            content_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[content_start:content_end].strip()

            chunks.append(
                Chunk(
                    id=f"{file_path.stem}-{uuid.uuid4().hex[:8]}",
                    source=str(file_path),
                    content=content,
                    header_level=level,
                    header_text=header_text,
                    tags=tags,
                )
            )

        return chunks


_INDEXER_MAP: dict[str, type] = {
    ".csv": CsvIndexer,
    ".md": MarkdownIndexer,
}


class Indexer:
    """Router that selects the appropriate indexer based on file extension."""

    def index_file(self, path: str) -> list[Document | Chunk]:
        """Index a file using the appropriate indexer.

        Args:
            path: Path to the file to index.

        Returns:
            A list of Document or Chunk objects.

        Raises:
            ValueError: If the file extension is unsupported.

        """
        ext = Path(path).suffix.lower()
        indexer_cls = _INDEXER_MAP.get(ext)
        if indexer_cls is None:
            msg = f"Unsupported file extension: {ext}"
            raise ValueError(msg)
        return indexer_cls().index_file(path)

    def index_directory(self, directory: str) -> list[Document | Chunk]:
        """Index all supported files in a directory recursively.

        Args:
            directory: Path to the directory.

        Returns:
            A combined list of Document and Chunk objects.

        """
        results: list[Document | Chunk] = []
        dir_path = Path(directory)

        # Recursively find all files with supported extensions
        for ext in _INDEXER_MAP:
            for file_path in sorted(dir_path.rglob(f"*{ext}")):
                if file_path.is_file():
                    results.extend(self.index_file(str(file_path)))

        return results
