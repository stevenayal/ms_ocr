"""Tests for CLI."""

import pytest
from click.testing import CliRunner

from ms_ocr.cli import cli


class TestCLI:
    """Test command-line interface."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "ms-ocr" in result.output

    def test_extract_help(self):
        """Test extract command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["extract", "--help"])

        assert result.exit_code == 0
        assert "--input" in result.output
        assert "--out" in result.output
        assert "--lang" in result.output

    def test_extract_missing_input(self):
        """Test extract command with missing input."""
        runner = CliRunner()
        result = runner.invoke(cli, ["extract", "--out", "output"])

        assert result.exit_code != 0

    def test_extract_missing_output(self):
        """Test extract command with missing output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["extract", "--input", "input.pdf"])

        assert result.exit_code != 0

    def test_version(self):
        """Test version flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output
