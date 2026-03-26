"""Prompt assembler module.

Provides functionality to format search results into LLM-friendly
prompt context in XML or Markdown format.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from omniskill.models import Chunk

if TYPE_CHECKING:
    from omniskill.models import SearchResult


class OutputFormat(Enum):
    """Supported output formats for prompt assembly."""

    XML = "xml"
    MARKDOWN = "markdown"
    LLMS_TXT = "llms_txt"


class PromptAssembler:
    """Assembles search results into formatted prompt context.

    Supports XML and Markdown output formats with proper structure
    and source attribution.
    """

    def __init__(self, max_context_length: int = 4000) -> None:
        """Initialize the assembler.

        Args:
            max_context_length: Maximum character length for output.
        """
        self.max_context_length = max_context_length

    def assemble(
        self,
        results: list[SearchResult],
        output_format: OutputFormat | str = OutputFormat.XML,
        include_metadata: bool = False,  # noqa: FBT001, FBT002
    ) -> str:
        """Assemble search results into formatted output.

        Args:
            results: Search results to format.
            output_format: Output format (XML or MARKDOWN).
            include_metadata: Whether to include BM25 scores and ranks.

        Returns:
            Formatted output string.

        Raises:
            ValueError: If output_format is invalid.
        """
        if isinstance(output_format, str):
            try:
                output_format = OutputFormat(output_format.lower())
            except ValueError:
                msg = f"Invalid output format: {output_format}. Use 'xml', 'markdown', or 'llms_txt'."
                raise ValueError(msg) from None

        if not results:
            return self._format_empty(output_format)

        # Separate CSV and Markdown results
        csv_results = []
        markdown_results = []

        for result in results:
            doc = result.document
            if doc.source.endswith(".csv"):
                csv_results.append(result)
            else:
                markdown_results.append(result)

        # Format based on output format
        if output_format == OutputFormat.XML:
            return self._format_xml(csv_results, markdown_results, include_metadata)
        if output_format == OutputFormat.LLMS_TXT:
            return self._format_llms_txt(csv_results, markdown_results)
        return self._format_markdown(csv_results, markdown_results, include_metadata)

    def _format_empty(self, output_format: OutputFormat) -> str:
        """Format empty results message.

        Args:
            output_format: Output format.

        Returns:
            Formatted empty message.
        """
        if output_format == OutputFormat.XML:
            return "<context_injection>\n  <message>No relevant context found.</message>\n</context_injection>"
        return "## Context\n\nNo relevant context found."

    def _format_xml(
        self,
        csv_results: list[SearchResult],
        markdown_results: list[SearchResult],
        include_metadata: bool,  # noqa: FBT001
    ) -> str:
        """Format results as XML.

        Args:
            csv_results: CSV search results.
            markdown_results: Markdown search results.
            include_metadata: Whether to include metadata.

        Returns:
            XML formatted string.
        """
        root = ET.Element("context_injection")

        # Add CSV results as rules
        if csv_results:
            rules_elem = ET.SubElement(root, "rules")
            # Group by source file
            by_source: dict[str, list[SearchResult]] = {}
            for result in csv_results:
                source = result.document.source
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(result)

            for source, source_results in by_source.items():
                source_elem = ET.SubElement(rules_elem, "source", file=source)
                for result in source_results:
                    doc = result.document
                    rule_elem = ET.SubElement(source_elem, "rule")
                    rule_elem.text = doc.content

                    if include_metadata:
                        rule_elem.set("score", f"{result.score:.4f}")
                        rule_elem.set("id", doc.id)

        # Add Markdown results as reference
        if markdown_results:
            reference_elem = ET.SubElement(root, "reference")
            for result in markdown_results:
                doc = result.document
                chunk = doc if isinstance(doc, Chunk) else None

                section_elem = ET.SubElement(
                    reference_elem,
                    "section",
                    source=doc.source,
                )

                if chunk and chunk.header_text:
                    section_elem.set("header", chunk.header_text)
                    if chunk.header_level:
                        section_elem.set("level", str(chunk.header_level))

                content_elem = ET.SubElement(section_elem, "content")
                content_elem.text = doc.content

                if include_metadata:
                    section_elem.set("score", f"{result.score:.4f}")
                    section_elem.set("id", doc.id)

        # Convert to string with proper formatting
        ET.indent(root, space="  ")
        output = ET.tostring(root, encoding="unicode", xml_declaration=False)

        # Truncate if necessary
        if len(output) > self.max_context_length:
            output = output[: self.max_context_length - 20] + "\n... [truncated]"

        return output

    def _format_markdown(
        self,
        csv_results: list[SearchResult],
        markdown_results: list[SearchResult],
        include_metadata: bool,  # noqa: FBT001
    ) -> str:
        """Format results as Markdown.

        Args:
            csv_results: CSV search results.
            markdown_results: Markdown search results.
            include_metadata: Whether to include metadata.

        Returns:
            Markdown formatted string.
        """
        lines: list[str] = ["## Context"]

        # Add CSV results as rules
        if csv_results:
            lines.append("\n### Rules")

            # Group by source file
            by_source: dict[str, list[SearchResult]] = {}
            for result in csv_results:
                source = result.document.source
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(result)

            for source, source_results in by_source.items():
                lines.append(f"\n**Source: {source}**\n")
                for result in source_results:
                    doc = result.document
                    line = f"- {doc.content}"
                    if include_metadata:
                        line += f" (score: {result.score:.4f})"
                    lines.append(line)

        # Add Markdown results as references
        if markdown_results:
            lines.append("\n### References")

            for result in markdown_results:
                doc = result.document
                chunk = doc if isinstance(doc, Chunk) else None

                lines.append(f"\n**Source: {doc.source}**")
                if chunk and chunk.header_text:
                    header_prefix = "#" * (chunk.header_level or 2)
                    lines.append(f"{header_prefix} {chunk.header_text}")

                if include_metadata:
                    lines.append(f"*Score: {result.score:.4f}*")

                lines.append(f"\n{doc.content}")

        output = "\n".join(lines)

        # Truncate if necessary
        if len(output) > self.max_context_length:
            output = output[: self.max_context_length - 20] + "\n\n... [truncated]"

        return output

    def _format_llms_txt(
        self,
        csv_results: list[SearchResult],
        markdown_results: list[SearchResult],
    ) -> str:
        """Format results in llms.txt style markdown.

        Follows the llms.txt spec: H1 title, blockquote summary,
        then H2 sections with content from matched documents.

        Args:
            csv_results: CSV search results.
            markdown_results: Markdown search results.

        Returns:
            llms.txt style markdown string.
        """
        lines: list[str] = [
            "# Search Results",
            "",
            "> Relevant context from the knowledge base.",
            "",
        ]

        # Group all results by source file
        by_source: dict[str, list[SearchResult]] = {}
        for result in csv_results + markdown_results:
            source = result.document.source
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(result)

        for source, source_results in by_source.items():
            # Determine section header from source filename
            filename = Path(source).stem.replace("_", " ").replace("-", " ").title()
            first = source_results[0].document
            chunk = first if isinstance(first, Chunk) else None

            if chunk and chunk.header_text:
                lines.append(f"## {chunk.header_text}")
            else:
                lines.append(f"## {filename}")
            lines.append("")

            for result in source_results:
                doc = result.document
                lines.append(doc.content)
                lines.append("")

        output = "\n".join(lines)

        if len(output) > self.max_context_length:
            output = output[: self.max_context_length - 20] + "\n\n... [truncated]"

        return output
