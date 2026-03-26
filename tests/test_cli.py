"""Tests for CLI module."""

from __future__ import annotations

import subprocess
import sys


def test_cli_runs() -> None:
    """Test that the CLI runs successfully."""
    result = subprocess.run(
        [sys.executable, "-m", "omniskill.cli", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "OmniSkill Framework" in result.stdout


def test_cli_create_command() -> None:
    """Test that the CLI create command works."""
    result = subprocess.run(
        [sys.executable, "-m", "omniskill.cli", "create", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Create a new OmniSkill" in result.stdout


def test_cli_search_command() -> None:
    """Test that the CLI search command works."""
    result = subprocess.run(
        [sys.executable, "-m", "omniskill.cli", "search", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Search skill knowledge base" in result.stdout
