"""Tests for career.py CLI tool."""

import json
import sys
from pathlib import Path
from unittest import mock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from career import cmd_new, cmd_validate  # noqa: E402


class TestCmdNew:
    """Tests for the 'new' command."""

    def test_creates_application_directory(self, tmp_path):
        """Test that new command creates proper directory structure."""
        with mock.patch("career.APPLICATIONS_DIR", tmp_path), mock.patch(
            "career.ROOT", tmp_path
        ):
            args = mock.Mock()
            args.company = "TestCorp"
            args.role = "Senior Engineer"

            result = cmd_new(args)

            assert result == 0
            # Find the created directory
            dirs = list(tmp_path.iterdir())
            assert len(dirs) == 1
            app_dir = dirs[0]
            assert "testcorp-senior-engineer" in app_dir.name
            assert (app_dir / "job_desc.md").exists()

    def test_creates_job_desc_with_frontmatter(self, tmp_path):
        """Test that job_desc.md has proper YAML frontmatter."""
        with mock.patch("career.APPLICATIONS_DIR", tmp_path), mock.patch(
            "career.ROOT", tmp_path
        ):
            args = mock.Mock()
            args.company = "Acme"
            args.role = "Developer"

            cmd_new(args)

            dirs = list(tmp_path.iterdir())
            job_desc = (dirs[0] / "job_desc.md").read_text()
            assert "company: Acme" in job_desc
            assert "role: Developer" in job_desc
            assert "status: draft" in job_desc

    def test_rejects_empty_company(self, tmp_path):
        """Test that empty company name is rejected."""
        with mock.patch("career.APPLICATIONS_DIR", tmp_path), mock.patch(
            "career.ROOT", tmp_path
        ), mock.patch("builtins.input", return_value=""):
            args = mock.Mock()
            args.company = ""
            args.role = "Developer"

            result = cmd_new(args)

            assert result == 1

    def test_rejects_duplicate_application(self, tmp_path):
        """Test that duplicate applications are rejected."""
        with mock.patch("career.APPLICATIONS_DIR", tmp_path), mock.patch(
            "career.ROOT", tmp_path
        ):
            args = mock.Mock()
            args.company = "DupeCorp"
            args.role = "Engineer"

            # Create first
            cmd_new(args)
            # Try to create duplicate
            result = cmd_new(args)

            assert result == 1


class TestCmdValidate:
    """Tests for the 'validate' command."""

    def test_validates_complete_setup(self, tmp_path):
        """Test validation passes with complete setup."""
        # Create required files
        source_dir = tmp_path / "source_materials"
        source_dir.mkdir()

        identity = {
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "location": "New York, NY",
        }
        (source_dir / "identity.json").write_text(json.dumps(identity))
        (source_dir / "master_experience.md").write_text(
            "# Experience\n\nReal content here."
        )

        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "style.tex").write_text("% LaTeX style")
        (templates_dir / "minimal.tex").write_text("% Minimal style")
        (templates_dir / "creative.tex").write_text("% Creative style")
        (templates_dir / "executive.tex").write_text("% Executive style")
        (templates_dir / "cover_letter_style.tex").write_text("% Cover letter style")

        with mock.patch("career.ROOT", tmp_path), mock.patch(
            "career.SOURCE_DIR", source_dir
        ), mock.patch("career.IDENTITY_JSON", source_dir / "identity.json"), mock.patch(
            "career.MASTER_EXP", source_dir / "master_experience.md"
        ):
            args = mock.Mock()
            result = cmd_validate(args)

            assert result == 0

    def test_detects_missing_identity(self, tmp_path):
        """Test validation fails when identity.json is missing."""
        source_dir = tmp_path / "source_materials"
        source_dir.mkdir()

        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "style.tex").write_text("% LaTeX style")
        (templates_dir / "cover_letter_style.tex").write_text("% Cover letter style")

        with mock.patch("career.ROOT", tmp_path), mock.patch(
            "career.SOURCE_DIR", source_dir
        ), mock.patch("career.IDENTITY_JSON", source_dir / "identity.json"), mock.patch(
            "career.MASTER_EXP", source_dir / "master_experience.md"
        ):
            args = mock.Mock()
            result = cmd_validate(args)

            assert result == 1

    def test_detects_placeholder_values(self, tmp_path):
        """Test validation warns on placeholder values."""
        source_dir = tmp_path / "source_materials"
        source_dir.mkdir()

        identity = {
            "full_name": "Your Name",
            "email": "your@email.com",
            "phone": "+1234567890",
            "location": "Your City",
        }
        (source_dir / "identity.json").write_text(json.dumps(identity))
        (source_dir / "master_experience.md").write_text("# Experience")

        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "style.tex").write_text("% LaTeX style")
        (templates_dir / "minimal.tex").write_text("% Minimal style")
        (templates_dir / "creative.tex").write_text("% Creative style")
        (templates_dir / "executive.tex").write_text("% Executive style")
        (templates_dir / "cover_letter_style.tex").write_text("% Cover letter style")

        with mock.patch("career.ROOT", tmp_path), mock.patch(
            "career.SOURCE_DIR", source_dir
        ), mock.patch("career.IDENTITY_JSON", source_dir / "identity.json"), mock.patch(
            "career.MASTER_EXP", source_dir / "master_experience.md"
        ):
            args = mock.Mock()
            # Should return 0 (warnings don't cause failure)
            result = cmd_validate(args)
            assert result == 0


class TestSlugGeneration:
    """Tests for application slug generation."""

    def test_slug_handles_special_characters(self, tmp_path):
        """Test that special characters are handled in slugs."""
        with mock.patch("career.APPLICATIONS_DIR", tmp_path), mock.patch(
            "career.ROOT", tmp_path
        ):
            args = mock.Mock()
            args.company = "Acme & Co."
            args.role = "Sr. Engineer (Remote)"

            cmd_new(args)

            dirs = list(tmp_path.iterdir())
            assert len(dirs) == 1
            # Should be sanitized
            assert "&" not in dirs[0].name
            assert "(" not in dirs[0].name

    def test_slug_handles_spaces(self, tmp_path):
        """Test that spaces are converted to hyphens."""
        with mock.patch("career.APPLICATIONS_DIR", tmp_path), mock.patch(
            "career.ROOT", tmp_path
        ):
            args = mock.Mock()
            args.company = "Big Tech Corp"
            args.role = "Staff Software Engineer"

            cmd_new(args)

            dirs = list(tmp_path.iterdir())
            assert " " not in dirs[0].name
            assert "big-tech-corp" in dirs[0].name
