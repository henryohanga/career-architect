# Contributing to Career Architect

First off, thank you for considering contributing to Career Architect! 🎉

This project helps engineers create better job applications using AI assistants. Your contributions help job seekers everywhere land their dream roles.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs what actually happened
- **Environment details** (OS, Python version, AI assistant used)
- **Screenshots** if applicable

### 💡 Suggesting Features

Feature suggestions are welcome! Please include:

- **Use case** - What problem does this solve?
- **Proposed solution** - How should it work?
- **Alternatives considered** - Other approaches you've thought about

### 📝 Improving Prompts

The `.prompts/` directory is the heart of this project. Prompt improvements that lead to better AI outputs are highly valued:

- Test your prompt changes with multiple AI assistants (Claude, GPT-4, etc.)
- Include before/after examples showing the improvement
- Ensure backward compatibility with existing workflows

### 📖 Documentation

Help make the project more accessible:

- Fix typos or unclear explanations
- Add examples and use cases
- Translate documentation
- Create video tutorials

### 🔧 Code Contributions

Good first issues are labeled `good first issue`. Areas where help is needed:

- **New output formats** (HTML resume, ATS-optimized text)
- **Template themes** (different LaTeX styles)
- **CLI improvements** (new commands, better UX)
- **Testing** (unit tests, integration tests)

## Development Setup

### Prerequisites

- Python 3.8+
- Pandoc
- LaTeX distribution
- Git

### Local Setup

```bash
# Fork and clone the repository
git clone https://github.com/henryohanga/career-architect.git
cd career-architect

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
make check
```

### Running Tests

```bash
# Run all unit tests
make test

# Run tests with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_career.py -v

# Run with coverage (if installed)
python -m pytest tests/ --cov=scripts
```

### Linting

```bash
# Check Python syntax
make lint

# Run flake8 directly
flake8 scripts/ --max-line-length=100 --ignore=E501,W503

# Validate project structure
python scripts/career.py validate
```

### ATS Scoring Tool

Test the ATS keyword analyzer:

```bash
# Score an application
python scripts/ats_score.py applications/your-application/

# JSON output for automation
python scripts/ats_score.py applications/your-application/ --json
```

## Pull Request Process

1. **Fork** the repository and create your branch from `main`
2. **Make changes** following our style guidelines
3. **Test** your changes thoroughly
4. **Update documentation** if needed
5. **Submit PR** with a clear description

### PR Title Format

Use conventional commits style:

- `feat: add new resume template`
- `fix: correct PDF margin issue`
- `docs: update installation guide`
- `refactor: simplify build script`

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-reviewed my changes
- [ ] Added/updated documentation as needed
- [ ] Tested with at least one AI assistant
- [ ] No breaking changes (or clearly documented)

## Style Guidelines

### Python Code

- Follow PEP 8 (we're lenient on line length up to 100 chars)
- Use type hints where helpful
- Include docstrings for functions
- Use meaningful variable names

### Markdown/Prompts

- Use clear, concise language
- Include examples where helpful
- Structure with headers for scannability
- Test prompts with multiple AI assistants

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep first line under 72 characters
- Reference issues when applicable

## Recognition

Contributors are recognized in:

- GitHub contributors list
- Release notes for significant contributions

## Questions?

Feel free to open an issue with the `question` label or start a discussion.

Thank you for contributing! 🙏
