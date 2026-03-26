"""Configuration management for OmniSkill framework.

Provides structured configuration using msgspec for validation
and serialization of framework settings.
"""

from __future__ import annotations

import os
from pathlib import Path

import msgspec


class OmniSkillConfig(msgspec.Struct):
    """Configuration for OmniSkill framework.

    Attributes:
        csv_extensions: Supported CSV file extensions.
        markdown_extensions: Supported Markdown file extensions.
        max_file_size_mb: Maximum file size in megabytes.
        default_search_limit: Default number of search results.
        bm25_k1: BM25 term frequency saturation parameter.
        bm25_b: BM25 length normalization parameter.
        default_output_format: Default output format (xml or markdown).
        max_context_length: Maximum context length in characters.
        skills_dir: Directory for skill files.
        core_dir: Directory for core modules.
    """

    # Indexing settings
    csv_extensions: tuple[str, ...] = (".csv",)
    markdown_extensions: tuple[str, ...] = (".md", ".markdown")
    max_file_size_mb: int = 10

    # Search settings
    default_search_limit: int = 10
    bm25_k1: float = 1.5
    bm25_b: float = 0.75

    # Assembly settings
    default_output_format: str = "xml"
    max_context_length: int = 4000

    # Paths
    skills_dir: Path = Path("skills")
    core_dir: Path = Path("core")

    @classmethod
    def from_file(cls, path: str | Path) -> OmniSkillConfig:
        """Load configuration from a TOML file.

        Args:
            path: Path to the configuration file.

        Returns:
            Configuration instance.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If the configuration file is invalid.
        """
        config_path = Path(path)
        if not config_path.exists():
            msg = f"Configuration file not found: {config_path}"
            raise FileNotFoundError(msg)

        try:
            import tomllib  # noqa: PLC0415

            with config_path.open("rb") as f:
                data = tomllib.load(f)
            return cls(**data)
        except Exception as e:
            msg = f"Invalid configuration file: {e}"
            raise ValueError(msg) from e

    @classmethod
    def from_env(cls) -> OmniSkillConfig:
        """Load configuration from environment variables.

        Returns:
            Configuration instance with values from environment.
        """
        config = cls()

        # Override with environment variables if present
        if limit := os.getenv("OMNISKILL_DEFAULT_SEARCH_LIMIT"):
            config = msgspec.structs.replace(config, default_search_limit=int(limit))

        if k1 := os.getenv("OMNISKILL_BM25_K1"):
            config = msgspec.structs.replace(config, bm25_k1=float(k1))

        if b := os.getenv("OMNISKILL_BM25_B"):
            config = msgspec.structs.replace(config, bm25_b=float(b))

        if output_format := os.getenv("OMNISKILL_DEFAULT_OUTPUT_FORMAT"):
            config = msgspec.structs.replace(config, default_output_format=output_format)

        if length := os.getenv("OMNISKILL_MAX_CONTEXT_LENGTH"):
            config = msgspec.structs.replace(config, max_context_length=int(length))

        if skills_dir := os.getenv("OMNISKILL_SKILLS_DIR"):
            config = msgspec.structs.replace(config, skills_dir=Path(skills_dir))

        return config

    def merge(self, other: OmniSkillConfig) -> OmniSkillConfig:
        """Merge another configuration into this one.

        Args:
            other: Configuration to merge.

        Returns:
            New configuration with merged values.
        """
        return msgspec.structs.replace(
            self,
            csv_extensions=other.csv_extensions or self.csv_extensions,
            markdown_extensions=other.markdown_extensions or self.markdown_extensions,
            max_file_size_mb=other.max_file_size_mb or self.max_file_size_mb,
            default_search_limit=other.default_search_limit or self.default_search_limit,
            bm25_k1=other.bm25_k1 or self.bm25_k1,
            bm25_b=other.bm25_b or self.bm25_b,
            default_output_format=other.default_output_format or self.default_output_format,
            max_context_length=other.max_context_length or self.max_context_length,
            skills_dir=other.skills_dir or self.skills_dir,
            core_dir=other.core_dir or self.core_dir,
        )
