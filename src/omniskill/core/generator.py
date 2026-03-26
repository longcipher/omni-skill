"""Skill generator module.

Analyzes dataset directories (CSV and Markdown files) and generates:
1. A Python processing script that uses the OmniSkill library
2. A SKILL.md document following the skill specification
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

import structlog

logger = structlog.get_logger()

_HEADER_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_MAX_SAMPLE_ROWS = 3
_MAX_SECTION_PREVIEW = 5
_MAX_SAMPLE_VALUE_LEN = 80


@dataclass(slots=True, frozen=True)
class CsvDatasetInfo:
    """Metadata extracted from a CSV file.

    Attributes:
        path: Relative path to the CSV file.
        columns: Column header names.
        row_count: Number of data rows.
        sample_rows: First few rows for preview.
    """

    path: str
    columns: tuple[str, ...]
    row_count: int
    sample_rows: tuple[dict[str, str], ...]


@dataclass(slots=True, frozen=True)
class MarkdownDatasetInfo:
    """Metadata extracted from a Markdown file.

    Attributes:
        path: Relative path to the Markdown file.
        sections: List of (level, header_text) tuples.
        char_count: Total character count of the content.
    """

    path: str
    sections: tuple[tuple[int, str], ...]
    char_count: int


@dataclass(slots=True)
class DatasetAnalysis:
    """Complete analysis of a dataset directory.

    Attributes:
        skill_name: Derived name for the skill.
        dataset_dir: Path to the dataset directory.
        csv_files: Information about CSV files found.
        markdown_files: Information about Markdown files found.
        total_documents: Estimated total searchable documents.
    """

    skill_name: str
    dataset_dir: Path
    csv_files: list[CsvDatasetInfo] = field(default_factory=list)
    markdown_files: list[MarkdownDatasetInfo] = field(default_factory=list)
    total_documents: int = 0


def analyze_dataset(dataset_dir: str | Path, skill_name: str | None = None) -> DatasetAnalysis:
    """Analyze a dataset directory and extract metadata.

    Args:
        dataset_dir: Path to the dataset directory containing CSV/MD files.
        skill_name: Optional skill name. Derived from directory name if not given.

    Returns:
        A DatasetAnalysis object with extracted metadata.

    Raises:
        ValueError: If the directory does not exist or is empty.
    """
    dir_path = Path(dataset_dir)
    if not dir_path.exists():
        msg = f"Dataset directory does not exist: {dataset_dir}"
        raise ValueError(msg)

    if not dir_path.is_dir():
        msg = f"Path is not a directory: {dataset_dir}"
        raise ValueError(msg)

    if skill_name is None:
        skill_name = dir_path.name

    analysis = DatasetAnalysis(skill_name=skill_name, dataset_dir=dir_path)

    # Scan CSV files
    for csv_path in sorted(dir_path.rglob("*.csv")):
        if csv_path.is_file():
            info = _analyze_csv(csv_path, dir_path)
            if info is not None:
                analysis.csv_files.append(info)
                analysis.total_documents += info.row_count

    # Scan Markdown files
    for md_path in sorted(dir_path.rglob("*.md")):
        if md_path.is_file():
            info = _analyze_markdown(md_path, dir_path)
            if info is not None:
                analysis.markdown_files.append(info)
                analysis.total_documents += max(len(info.sections), 1)

    if not analysis.csv_files and not analysis.markdown_files:
        msg = f"No CSV or Markdown files found in: {dataset_dir}"
        raise ValueError(msg)

    logger.info(
        "dataset_analyzed",
        skill_name=skill_name,
        csv_count=len(analysis.csv_files),
        markdown_count=len(analysis.markdown_files),
        total_documents=analysis.total_documents,
    )

    return analysis


def _analyze_csv(csv_path: Path, base_dir: Path) -> CsvDatasetInfo | None:
    """Analyze a single CSV file.

    Args:
        csv_path: Path to the CSV file.
        base_dir: Base directory for computing relative paths.

    Returns:
        CsvDatasetInfo or None if the file cannot be parsed.
    """
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return None

            columns = tuple(reader.fieldnames)
            sample_rows: list[dict[str, str]] = []
            row_count = 0

            for row in reader:
                row_count += 1
                if len(sample_rows) < _MAX_SAMPLE_ROWS:
                    sample_rows.append({k: str(v)[:_MAX_SAMPLE_VALUE_LEN] for k, v in row.items()})

        rel_path = str(csv_path.relative_to(base_dir))
        return CsvDatasetInfo(
            path=rel_path,
            columns=columns,
            row_count=row_count,
            sample_rows=tuple(sample_rows),
        )
    except (csv.Error, OSError):
        return None


def _analyze_markdown(md_path: Path, base_dir: Path) -> MarkdownDatasetInfo | None:
    """Analyze a single Markdown file.

    Args:
        md_path: Path to the Markdown file.
        base_dir: Base directory for computing relative paths.

    Returns:
        MarkdownDatasetInfo or None if the file cannot be read.
    """
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return None

    if not text.strip():
        return None

    sections: list[tuple[int, str]] = []
    for match in _HEADER_RE.finditer(text):
        level = len(match.group(1))
        header_text = match.group(2).strip()
        sections.append((level, header_text))

    rel_path = str(md_path.relative_to(base_dir))
    return MarkdownDatasetInfo(
        path=rel_path,
        sections=tuple(sections),
        char_count=len(text),
    )


def generate_skill_script(
    analysis: DatasetAnalysis,
    output_dir: str | Path | None = None,
) -> str:
    """Generate a Python processing script for a skill.

    The generated script uses OmniSkill's SearchEngine and PromptAssembler
    to index, search, filter, and assemble results from the dataset.

    Args:
        analysis: Dataset analysis result.
        output_dir: Optional directory to write the script to.

    Returns:
        The generated Python script as a string.
    """
    script = _build_skill_script(analysis)

    if output_dir is not None:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        script_path = out_path / "search.py"
        script_path.write_text(script, encoding="utf-8")
        logger.info("skill_script_generated", path=str(script_path))

    return script


def generate_skill_md(
    analysis: DatasetAnalysis,
    output_dir: str | Path | None = None,
) -> str:
    """Generate a SKILL.md document for a skill.

    The SKILL.md follows the skill specification and instructs LLMs
    on how to use the skill's knowledge retrieval capabilities.

    Args:
        analysis: Dataset analysis result.
        output_dir: Optional directory to write SKILL.md to.

    Returns:
        The generated SKILL.md content as a string.
    """
    md = _build_skill_md(analysis)

    if output_dir is not None:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        md_path = out_path / "SKILL.md"
        md_path.write_text(md, encoding="utf-8")
        logger.info("skill_md_generated", path=str(md_path))

    return md


def generate_skill(
    dataset_dir: str | Path,
    skill_name: str | None = None,
    output_dir: str | Path | None = None,
) -> DatasetAnalysis:
    """Generate a complete skill from a dataset directory.

    Creates the skill directory structure with:
    - search.py: Python processing script using OmniSkill
    - SKILL.md: Skill specification document
    - datasets/: Symlink or copy of source datasets

    Args:
        dataset_dir: Path to the source dataset directory.
        skill_name: Optional skill name. Derived from directory name if not given.
        output_dir: Optional output directory. Defaults to skills/<skill_name>/.

    Returns:
        The dataset analysis used for generation.

    Raises:
        ValueError: If the dataset directory is invalid or empty.
    """
    analysis = analyze_dataset(dataset_dir, skill_name)

    if output_dir is None:
        output_dir = Path("skills") / analysis.skill_name

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Generate script
    generate_skill_script(analysis, out_path)

    # Generate SKILL.md
    generate_skill_md(analysis, out_path)

    # Create datasets directory with symlink to source
    datasets_link = out_path / "datasets"
    if not datasets_link.exists():
        try:
            datasets_link.symlink_to(analysis.dataset_dir.resolve())
        except OSError:
            # Fallback: create directory and note it
            datasets_link.mkdir(exist_ok=True)

    logger.info(
        "skill_generated",
        skill_name=analysis.skill_name,
        output_dir=str(out_path),
    )

    return analysis


# ---------------------------------------------------------------------------
# Template builders
# ---------------------------------------------------------------------------

_SCRIPT_TEMPLATE = '''\
"""{skill_name} - OmniSkill search script.

Auto-generated by OmniSkill for the '{skill_name}' skill.
Searches the knowledge base and outputs results in llms.txt format.
"""

from __future__ import annotations

from pathlib import Path

from omniskill.core.assembler import OutputFormat, PromptAssembler
from omniskill.core.engine import SearchEngine


DATASET_DIR = Path(__file__).parent / "datasets"


def create_engine() -> SearchEngine:
    """Create and index a SearchEngine from the dataset directory."""
    engine = SearchEngine()
    engine.index_directory(DATASET_DIR)
    return engine


def search(query: str, limit: int = 10) -> str:
    """Search the knowledge base and return llms.txt formatted context."""
    engine = create_engine()
    results = engine.search(query, limit=limit)
    assembler = PromptAssembler()
    return assembler.assemble(results, output_format=OutputFormat.LLMS_TXT)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search the knowledge base.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    args = parser.parse_args()

    print(search(args.query, limit=args.limit))
'''


def _build_skill_script(analysis: DatasetAnalysis) -> str:
    """Build the Python search script content.

    Args:
        analysis: Dataset analysis result.

    Returns:
        Python script content as a string.
    """
    return _SCRIPT_TEMPLATE.format(skill_name=analysis.skill_name)


def _build_skill_md(analysis: DatasetAnalysis) -> str:
    """Build the SKILL.md content.

    Args:
        analysis: Dataset analysis result.

    Returns:
        SKILL.md content as a string.
    """
    skill_name = analysis.skill_name
    display_name = skill_name.replace("-", " ").replace("_", " ").title()
    module_name = skill_name.replace("-", "_")
    script_path = f"{module_name}/search.py"

    sections = [
        f"# {display_name}",
        "",
        "## Role",
        "",
        (
            f"You are a specialized assistant with expertise in {display_name.lower()}. "
            "You have access to a curated knowledge base that you can search to provide "
            "accurate, context-grounded answers."
        ),
        "",
        "## Knowledge Retrieval Action",
        "",
        "When you need information to answer a question, execute the following command:",
        "",
        "```bash",
        f'python {script_path} "<your query>"',
        "```",
        "",
        "The command returns the relevant context from the knowledge base.",
        "",
        "## Dataset Summary",
        "",
        _format_dataset_summary(analysis),
        f"**Total searchable documents**: ~{analysis.total_documents}",
        "",
        _INSTRUCTIONS_SECTION,
        "",
        "## Example Usage",
        "",
        f'User: "What are the best practices for {display_name.lower()}?"',
        "",
        "Action:",
        "```bash",
        f'python {script_path} "best practices"',
        "```",
        "",
        "Then use the returned context to answer the question.",
        "",
    ]
    return "\n".join(sections)


_INSTRUCTIONS_SECTION = """\
## Instructions

1. **Extract Keywords**: Identify the key concepts and terms from the user's question.

2. **Execute Search**: Run the search script with extracted keywords to
   retrieve relevant context from the knowledge base.

3. **Read Context**: Parse the returned context to understand the available
   information.

4. **Generate Response**: Use the retrieved context to provide an accurate,
   helpful response. Always cite your sources when using information from
   the knowledge base.

5. **Handle Missing Information**: If the search returns no results or
   insufficient information, acknowledge what you don't know and suggest
   alternative approaches."""


def _format_dataset_summary(analysis: DatasetAnalysis) -> str:
    """Format the dataset summary section for SKILL.md.

    Args:
        analysis: Dataset analysis result.

    Returns:
        Formatted dataset summary string.
    """
    parts: list[str] = []

    if analysis.csv_files:
        parts.append(f"### CSV Datasets ({len(analysis.csv_files)} files)\n")
        parts.extend(
            f"- **{ci.path}**: {ci.row_count} rows, columns: {', '.join(ci.columns)}" for ci in analysis.csv_files
        )
        parts.append("")

    if analysis.markdown_files:
        parts.append(f"### Markdown Datasets ({len(analysis.markdown_files)} files)\n")
        for md_info in analysis.markdown_files:
            section_names = [h for _, h in md_info.sections[:_MAX_SECTION_PREVIEW]]
            summary = ", ".join(section_names)
            if len(md_info.sections) > _MAX_SECTION_PREVIEW:
                summary += f", ... ({len(md_info.sections)} sections total)"
            parts.append(f"- **{md_info.path}**: {summary}")
        parts.append("")

    return "\n".join(parts)
