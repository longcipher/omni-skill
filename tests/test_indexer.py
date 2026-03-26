"""Tests for the Indexer module."""

from __future__ import annotations

import csv
import io
from pathlib import Path  # noqa: TC003

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from omniskill.core.indexer import CsvIndexer, Indexer, MarkdownIndexer
from omniskill.models import Chunk, Document

# ---------------------------------------------------------------------------
# CSV Indexer Tests
# ---------------------------------------------------------------------------


class TestCsvIndexer:
    """Tests for CsvIndexer."""

    def test_index_simple_csv(self, tmp_path: Path) -> None:
        csv_content = "name,age,city\nAlice,30,NYC\nBob,25,LA\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        indexer = CsvIndexer()
        docs = indexer.index_file(str(csv_file))

        assert len(docs) == 2
        assert all(isinstance(d, Document) for d in docs)
        assert docs[0].metadata["name"] == "Alice"
        assert docs[0].metadata["age"] == "30"
        assert docs[0].metadata["city"] == "NYC"
        assert docs[1].metadata["name"] == "Bob"
        assert docs[1].source == str(csv_file)

    def test_index_csv_single_row(self, tmp_path: Path) -> None:
        csv_content = "id,value\n1,hello\n"
        csv_file = tmp_path / "single.csv"
        csv_file.write_text(csv_content)

        indexer = CsvIndexer()
        docs = indexer.index_file(str(csv_file))

        assert len(docs) == 1
        assert docs[0].metadata["id"] == "1"
        assert docs[0].metadata["value"] == "hello"

    def test_index_csv_empty_file(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        indexer = CsvIndexer()
        docs = indexer.index_file(str(csv_file))

        assert len(docs) == 0

    def test_index_csv_header_only(self, tmp_path: Path) -> None:
        csv_content = "col1,col2,col3\n"
        csv_file = tmp_path / "header_only.csv"
        csv_file.write_text(csv_content)

        indexer = CsvIndexer()
        docs = indexer.index_file(str(csv_file))

        assert len(docs) == 0

    def test_index_csv_malformed(self, tmp_path: Path) -> None:
        csv_content = 'a,b\n1,"unclosed quote\n2,ok\n'
        csv_file = tmp_path / "malformed.csv"
        csv_file.write_text(csv_content)

        indexer = CsvIndexer()
        docs = indexer.index_file(str(csv_file))

        assert len(docs) >= 1

    def test_index_csv_content_field(self, tmp_path: Path) -> None:
        csv_content = "title,body\nFirst,Hello World\n"
        csv_file = tmp_path / "content.csv"
        csv_file.write_text(csv_content)

        indexer = CsvIndexer()
        docs = indexer.index_file(str(csv_file))

        assert "First" in docs[0].content
        assert "Hello World" in docs[0].content

    def test_index_csv_id_generation(self, tmp_path: Path) -> None:
        csv_content = "name,val\na,1\nb,2\n"
        csv_file = tmp_path / "ids.csv"
        csv_file.write_text(csv_content)

        indexer = CsvIndexer()
        docs = indexer.index_file(str(csv_file))

        ids = [d.id for d in docs]
        assert len(set(ids)) == 2

    def test_index_csv_unicode(self, tmp_path: Path) -> None:
        csv_content = "name,desc\n日本語,テスト\n"
        csv_file = tmp_path / "unicode.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        indexer = CsvIndexer()
        docs = indexer.index_file(str(csv_file))

        assert len(docs) == 1
        assert docs[0].metadata["name"] == "日本語"


# ---------------------------------------------------------------------------
# Markdown Indexer Tests
# ---------------------------------------------------------------------------


class TestMarkdownIndexer:
    """Tests for MarkdownIndexer."""

    def test_index_markdown_h2_chunks(self, tmp_path: Path) -> None:
        md_content = """## Section 1

Content for section 1.

## Section 2

Content for section 2.
"""
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content)

        indexer = MarkdownIndexer()
        chunks = indexer.index_file(str(md_file))

        assert len(chunks) == 2
        assert all(isinstance(c, Chunk) for c in chunks)
        assert chunks[0].header_level == 2
        assert chunks[0].header_text == "Section 1"
        assert chunks[1].header_level == 2
        assert chunks[1].header_text == "Section 2"

    def test_index_markdown_h3_chunks(self, tmp_path: Path) -> None:
        md_content = """## Main

### Sub 1

Details one.

### Sub 2

Details two.
"""
        md_file = tmp_path / "h3.md"
        md_file.write_text(md_content)

        indexer = MarkdownIndexer()
        chunks = indexer.index_file(str(md_file))

        assert len(chunks) == 3
        h3_chunks = [c for c in chunks if c.header_level == 3]
        assert len(h3_chunks) == 2
        assert h3_chunks[0].header_text == "Sub 1"
        assert h3_chunks[1].header_text == "Sub 2"

    def test_index_markdown_mixed_headers(self, tmp_path: Path) -> None:
        md_content = """## Top

Content top.

### Sub A

Content sub a.

## Second Top

Content second.

### Sub B

Content sub b.
"""
        md_file = tmp_path / "mixed.md"
        md_file.write_text(md_content)

        indexer = MarkdownIndexer()
        chunks = indexer.index_file(str(md_file))

        headers = [(c.header_level, c.header_text) for c in chunks]
        assert (2, "Top") in headers
        assert (3, "Sub A") in headers
        assert (2, "Second Top") in headers
        assert (3, "Sub B") in headers

    def test_index_markdown_no_headers(self, tmp_path: Path) -> None:
        md_content = "Just some text without any headers.\nMore text.\n"
        md_file = tmp_path / "noheaders.md"
        md_file.write_text(md_file.read_text() if md_file.exists() else md_content)
        md_file.write_text(md_content)

        indexer = MarkdownIndexer()
        chunks = indexer.index_file(str(md_file))

        assert len(chunks) == 1
        assert chunks[0].header_level is None
        assert chunks[0].header_text is None

    def test_index_markdown_empty_file(self, tmp_path: Path) -> None:
        md_file = tmp_path / "empty.md"
        md_file.write_text("")

        indexer = MarkdownIndexer()
        chunks = indexer.index_file(str(md_file))

        assert len(chunks) == 0

    def test_index_markdown_content_preserved(self, tmp_path: Path) -> None:
        md_content = """## Section

Line 1.
Line 2.

"""
        md_file = tmp_path / "content.md"
        md_file.write_text(md_content)

        indexer = MarkdownIndexer()
        chunks = indexer.index_file(str(md_file))

        assert "Line 1." in chunks[0].content
        assert "Line 2." in chunks[0].content

    def test_index_markdown_source_set(self, tmp_path: Path) -> None:
        md_content = "## Test\nContent\n"
        md_file = tmp_path / "source.md"
        md_file.write_text(md_content)

        indexer = MarkdownIndexer()
        chunks = indexer.index_file(str(md_file))

        assert chunks[0].source == str(md_file)

    def test_index_markdown_tags_empty(self, tmp_path: Path) -> None:
        md_content = "## Section\nText\n"
        md_file = tmp_path / "tags.md"
        md_file.write_text(md_content)

        indexer = MarkdownIndexer()
        chunks = indexer.index_file(str(md_file))

        assert chunks[0].tags == ()


# ---------------------------------------------------------------------------
# Indexer Router Tests
# ---------------------------------------------------------------------------


class TestIndexer:
    """Tests for the Indexer router class."""

    def test_indexer_selects_csv(self, tmp_path: Path) -> None:
        csv_content = "a,b\n1,2\n"
        csv_file = tmp_path / "data.csv"
        csv_file.write_text(csv_content)

        indexer = Indexer()
        result = indexer.index_file(str(csv_file))

        assert len(result) == 1
        assert isinstance(result[0], Document)

    def test_indexer_selects_markdown(self, tmp_path: Path) -> None:
        md_content = "## Header\nContent\n"
        md_file = tmp_path / "doc.md"
        md_file.write_text(md_content)

        indexer = Indexer()
        result = indexer.index_file(str(md_file))

        assert len(result) == 1
        assert isinstance(result[0], Chunk)

    def test_indexer_unsupported_extension(self, tmp_path: Path) -> None:
        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("hello")

        indexer = Indexer()
        with pytest.raises(ValueError, match="Unsupported"):
            indexer.index_file(str(txt_file))

    def test_indexer_index_directory(self, tmp_path: Path) -> None:
        (tmp_path / "a.csv").write_text("x\n1\n")
        (tmp_path / "b.md").write_text("## H\nText\n")

        indexer = Indexer()
        results = indexer.index_directory(str(tmp_path))

        types = {type(r) for r in results}
        assert Document in types
        assert Chunk in types


# ---------------------------------------------------------------------------
# Hypothesis Property Tests
# ---------------------------------------------------------------------------


class TestCsvPropertyTests:
    """Property-based tests for CSV indexing."""

    @given(
        headers=st.lists(
            st.text(min_size=1, alphabet="abcdefghijklmnopqrstuvwxyz"),
            min_size=1,
            max_size=5,
            unique=True,
        ),
        num_rows=st.integers(min_value=0, max_value=20),
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_csv_row_count_matches(self, tmp_path: Path, headers: list[str], num_rows: int) -> None:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for i in range(num_rows):
            writer.writerow([f"val_{i}_{h}" for h in headers])

        csv_file = tmp_path / "prop.csv"
        csv_file.write_text(output.getvalue())

        indexer = CsvIndexer()
        docs = indexer.index_file(str(csv_file))

        assert len(docs) == num_rows
        for doc in docs:
            assert isinstance(doc, Document)
            for h in headers:
                assert h in doc.metadata

    @given(
        data=st.lists(
            st.lists(st.text(min_size=0, max_size=20), min_size=2, max_size=4),
            min_size=1,
            max_size=10,
        )
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_csv_metadata_keys_present(self, tmp_path: Path, data: list[list[str]]) -> None:
        headers = [f"col{i}" for i in range(len(data[0]))]
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row[: len(headers)])

        csv_file = tmp_path / "prop2.csv"
        csv_file.write_text(output.getvalue())

        indexer = CsvIndexer()
        docs = indexer.index_file(str(csv_file))

        assert len(docs) == len(data)
        for doc in docs:
            for h in headers:
                assert h in doc.metadata


class TestMarkdownPropertyTests:
    """Property-based tests for Markdown indexing."""

    @given(
        headers=st.lists(
            st.text(
                min_size=1,
                max_size=20,
                alphabet="abcdefghijklmnopqrstuvwxyz ",
            ).map(str.strip),
            min_size=1,
            max_size=5,
        )
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_markdown_chunk_count_matches_headers(self, tmp_path: Path, headers: list[str]) -> None:
        parts = [f"## {h}\n\nContent for {h}.\n" for h in headers if h]

        md_file = tmp_path / "prop.md"
        md_file.write_text("\n".join(parts))

        indexer = MarkdownIndexer()
        chunks = indexer.index_file(str(md_file))

        non_empty_headers = [h for h in headers if h]
        assert len(chunks) == len(non_empty_headers)
        for chunk in chunks:
            assert isinstance(chunk, Chunk)
            assert chunk.header_text is not None

    @given(
        level=st.integers(min_value=2, max_value=3),
        title=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz"),
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_markdown_header_level_preserved(self, tmp_path: Path, level: int, title: str) -> None:
        prefix = "#" * level
        md_content = f"{prefix} {title}\n\nContent here.\n"
        md_file = tmp_path / "level.md"
        md_file.write_text(md_content)

        indexer = MarkdownIndexer()
        chunks = indexer.index_file(str(md_file))

        assert len(chunks) == 1
        assert chunks[0].header_level == level
        assert chunks[0].header_text == title
