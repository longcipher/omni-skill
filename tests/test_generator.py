"""Tests for the skill generator module."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from omniskill.core.generator import (
    _analyze_csv,
    _analyze_markdown,
    _build_skill_md,
    _build_skill_script,
    analyze_dataset,
    generate_skill,
    generate_skill_md,
    generate_skill_script,
)


@pytest.fixture
def sample_dataset_dir(tmp_path: Path) -> Path:
    """Create a temporary dataset directory with CSV and Markdown files."""
    # Create a CSV file
    csv_path = tmp_path / "api_patterns.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["pattern", "description", "example"])
        writer.writerow(["snake_case", "Use snake_case for endpoints", "/api/v1/user_profiles"])
        writer.writerow(["versioning", "Include API version in URL", "/api/v1/users"])
        writer.writerow(["pagination", "Use cursor-based pagination", "?cursor=abc&limit=20"])

    # Create a Markdown file
    md_path = tmp_path / "best_practices.md"
    md_path.write_text(
        "## Authentication\n\n"
        "Use JWT tokens for API authentication.\n\n"
        "### Token Generation\n\n"
        "Create tokens with expiration.\n\n"
        "## Error Handling\n\n"
        "Return consistent error responses.\n",
        encoding="utf-8",
    )

    # Create a second Markdown file
    md2_path = tmp_path / "guides.md"
    md2_path.write_text(
        "## Getting Started\n\n"
        "Follow these steps to set up the project.\n\n"
        "### Installation\n\n"
        "```bash\npip install mypackage\n```\n",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture
def csv_only_dataset_dir(tmp_path: Path) -> Path:
    """Create a dataset directory with only CSV files."""
    csv_path = tmp_path / "data.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "value"])
        writer.writerow(["alpha", "100"])
        writer.writerow(["beta", "200"])
    return tmp_path


@pytest.fixture
def md_only_dataset_dir(tmp_path: Path) -> Path:
    """Create a dataset directory with only Markdown files."""
    md_path = tmp_path / "docs.md"
    md_path.write_text(
        "# Overview\n\nSome intro text.\n\n## Section A\n\nDetails about A.\n\n## Section B\n\nDetails about B.\n",
        encoding="utf-8",
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Dataset Analysis Tests
# ---------------------------------------------------------------------------


class TestAnalyzeDataset:
    """Tests for analyze_dataset function."""

    def test_analyze_mixed_dataset(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        assert analysis.skill_name == "test-skill"
        assert len(analysis.csv_files) == 1
        assert len(analysis.markdown_files) == 2
        assert analysis.total_documents > 0

    def test_analyze_csv_only(self, csv_only_dataset_dir: Path) -> None:
        analysis = analyze_dataset(csv_only_dataset_dir)
        assert len(analysis.csv_files) == 1
        assert len(analysis.markdown_files) == 0

    def test_analyze_markdown_only(self, md_only_dataset_dir: Path) -> None:
        analysis = analyze_dataset(md_only_dataset_dir)
        assert len(analysis.csv_files) == 0
        assert len(analysis.markdown_files) == 1

    def test_analyze_derives_skill_name(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir)
        assert analysis.skill_name == sample_dataset_dir.name

    def test_analyze_nonexistent_dir_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="does not exist"):
            analyze_dataset(tmp_path / "nonexistent")

    def test_analyze_file_path_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("hi")
        with pytest.raises(ValueError, match="not a directory"):
            analyze_dataset(f)

    def test_analyze_empty_dir_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="No CSV or Markdown"):
            analyze_dataset(tmp_path)


class TestAnalyzeCsv:
    """Tests for _analyze_csv helper."""

    def test_extracts_columns(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["col_a", "col_b", "col_c"])
            writer.writerow(["1", "2", "3"])
        info = _analyze_csv(csv_path, tmp_path)
        assert info is not None
        assert info.columns == ("col_a", "col_b", "col_c")
        assert info.row_count == 1

    def test_counts_rows(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id"])
            for i in range(100):
                writer.writerow([str(i)])
        info = _analyze_csv(csv_path, tmp_path)
        assert info is not None
        assert info.row_count == 100

    def test_returns_sample_rows(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name"])
            for i in range(10):
                writer.writerow([f"item{i}"])
        info = _analyze_csv(csv_path, tmp_path)
        assert info is not None
        assert len(info.sample_rows) == 3

    def test_empty_csv_returns_none(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("")
        info = _analyze_csv(csv_path, tmp_path)
        assert info is None


class TestAnalyzeMarkdown:
    """Tests for _analyze_markdown helper."""

    def test_extracts_sections(self, tmp_path: Path) -> None:
        md_path = tmp_path / "test.md"
        md_path.write_text("## First\n\nContent.\n\n## Second\n\nMore.\n")
        info = _analyze_markdown(md_path, tmp_path)
        assert info is not None
        assert len(info.sections) == 2
        assert info.sections[0] == (2, "First")
        assert info.sections[1] == (2, "Second")

    def test_extracts_mixed_header_levels(self, tmp_path: Path) -> None:
        md_path = tmp_path / "test.md"
        md_path.write_text("# Title\n\n## Sub\n\n### SubSub\n\n")
        info = _analyze_markdown(md_path, tmp_path)
        assert info is not None
        assert len(info.sections) == 3
        assert info.sections[0] == (1, "Title")
        assert info.sections[1] == (2, "Sub")
        assert info.sections[2] == (3, "SubSub")

    def test_empty_md_returns_none(self, tmp_path: Path) -> None:
        md_path = tmp_path / "empty.md"
        md_path.write_text("")
        info = _analyze_markdown(md_path, tmp_path)
        assert info is None

    def test_char_count(self, tmp_path: Path) -> None:
        content = "## Header\n\nSome text.\n"
        md_path = tmp_path / "test.md"
        md_path.write_text(content)
        info = _analyze_markdown(md_path, tmp_path)
        assert info is not None
        assert info.char_count == len(content)


# ---------------------------------------------------------------------------
# Script Generation Tests
# ---------------------------------------------------------------------------


class TestBuildSkillScript:
    """Tests for the generated Python script."""

    def test_script_contains_imports(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        script = _build_skill_script(analysis)
        assert "from omniskill.core.engine import SearchEngine" in script
        assert "from omniskill.core.assembler import OutputFormat, PromptAssembler" in script

    def test_script_contains_search_function(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        script = _build_skill_script(analysis)
        assert "def search(query: str, limit: int = 10) -> str:" in script

    def test_script_uses_llms_txt_format(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        script = _build_skill_script(analysis)
        assert "OutputFormat.LLMS_TXT" in script

    def test_script_main_block(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        script = _build_skill_script(analysis)
        assert 'if __name__ == "__main__":' in script

    def test_script_valid_python(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        script = _build_skill_script(analysis)
        compile(script, "<test>", "exec")


class TestGenerateSkillScript:
    """Tests for generate_skill_script function."""

    def test_writes_file(self, sample_dataset_dir: Path, tmp_path: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        result = generate_skill_script(analysis, tmp_path)
        script_path = tmp_path / "search.py"
        assert script_path.exists()
        assert script_path.read_text() == result

    def test_returns_string_without_output_dir(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        result = generate_skill_script(analysis)
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# SKILL.md Generation Tests
# ---------------------------------------------------------------------------


class TestBuildSkillMd:
    """Tests for the generated SKILL.md content."""

    def test_contains_title(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        md = _build_skill_md(analysis)
        assert "# Test Skill" in md

    def test_contains_role_section(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        md = _build_skill_md(analysis)
        assert "## Role" in md

    def test_contains_knowledge_retrieval(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        md = _build_skill_md(analysis)
        assert "## Knowledge Retrieval Action" in md
        assert "python" in md
        assert "search.py" in md

    def test_contains_dataset_summary(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        md = _build_skill_md(analysis)
        assert "## Dataset Summary" in md
        assert "CSV Datasets" in md
        assert "Markdown Datasets" in md

    def test_contains_instructions(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        md = _build_skill_md(analysis)
        assert "## Instructions" in md
        assert "Extract Keywords" in md

    def test_csv_only_has_no_markdown_section(self, csv_only_dataset_dir: Path) -> None:
        analysis = analyze_dataset(csv_only_dataset_dir, skill_name="csv-skill")
        md = _build_skill_md(analysis)
        assert "CSV Datasets" in md
        assert "Markdown Datasets" not in md

    def test_md_only_has_no_csv_section(self, md_only_dataset_dir: Path) -> None:
        analysis = analyze_dataset(md_only_dataset_dir, skill_name="md-skill")
        md = _build_skill_md(analysis)
        assert "Markdown Datasets" in md
        assert "CSV Datasets" not in md


class TestGenerateSkillMd:
    """Tests for generate_skill_md function."""

    def test_writes_file(self, sample_dataset_dir: Path, tmp_path: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        result = generate_skill_md(analysis, tmp_path)
        md_path = tmp_path / "SKILL.md"
        assert md_path.exists()
        assert md_path.read_text() == result

    def test_returns_string_without_output_dir(self, sample_dataset_dir: Path) -> None:
        analysis = analyze_dataset(sample_dataset_dir, skill_name="test-skill")
        result = generate_skill_md(analysis)
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# Full Generation Tests
# ---------------------------------------------------------------------------


class TestGenerateSkill:
    """Tests for the full generate_skill function."""

    def test_creates_full_skill_structure(self, sample_dataset_dir: Path, tmp_path: Path) -> None:
        output_dir = tmp_path / "generated-skill"
        analysis = generate_skill(
            dataset_dir=sample_dataset_dir,
            skill_name="my-skill",
            output_dir=output_dir,
        )

        assert analysis.skill_name == "my-skill"
        assert (output_dir / "SKILL.md").exists()
        assert (output_dir / "search.py").exists()
        assert (output_dir / "datasets").exists()

    def test_generated_search_is_valid_python(self, sample_dataset_dir: Path, tmp_path: Path) -> None:
        output_dir = tmp_path / "skill"
        generate_skill(
            dataset_dir=sample_dataset_dir,
            skill_name="test",
            output_dir=output_dir,
        )
        script = (output_dir / "search.py").read_text()
        compile(script, "<test>", "exec")
