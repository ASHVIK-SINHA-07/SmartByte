# Contributing to Smart Study Assistant

First off, thank you for considering contributing to Smart Study Assistant! 🎉

It's people like you that make Smart Study Assistant such a great tool for students everywhere.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Process](#development-process)
- [Style Guidelines](#style-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)

---

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of:
- Age, body size, disability
- Ethnicity, gender identity and expression
- Level of experience, education, socio-economic status
- Nationality, personal appearance, race, religion
- Sexual identity and orientation

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git installed on your system
- A GitHub account
- Gemini API key (for testing AI features)

### Setup Development Environment

1. Fork the repository on GitHub

2. Clone your fork:
```bash
git clone https://github.com/YOUR-USERNAME/my-first-repo.git
cd my-first-repo/Smart_byte
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/ASHVIK-SINHA-07/my-first-repo.git
```

4. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

5. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

6. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

7. Run the application:
```bash
python main.py
```

---

## 🤝 How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check the existing issues. When creating a bug report, include:

- **Clear title** - Use a clear and descriptive title
- **Steps to reproduce** - Detailed steps to reproduce the issue
- **Expected behavior** - What you expected to happen
- **Actual behavior** - What actually happened
- **Screenshots** - If applicable
- **Environment** - OS, Python version, etc.
- **Logs** - Relevant log entries from `logs/app.log`

**Template:**
```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
Add screenshots if applicable.

**Environment:**
- OS: [e.g., Windows 11, macOS 14, Ubuntu 22.04]
- Python Version: [e.g., 3.11.5]
- App Version: [e.g., 2.0.0]

**Additional Context**
Any other context about the problem.
```

### Suggesting Enhancements 💡

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** - Use a clear and descriptive title
- **Detailed description** - Provide a detailed description
- **Current behavior** - Describe the current behavior
- **Desired behavior** - Describe the desired behavior
- **Why is this useful?** - Explain the benefit
- **Examples** - Provide examples if possible

### Pull Requests 🔨

- Fill in the required template
- Follow the style guidelines
- Include appropriate tests
- Update documentation
- End all files with a newline

---

## 💻 Development Process

### 1. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/amazing-feature
# or
git checkout -b bugfix/fix-something
# or
git checkout -b docs/update-readme
```

**Branch naming conventions:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests
- `chore/` - Maintenance tasks

### 2. Make Your Changes

- Write clean, readable code
- Follow the style guidelines
- Add comments for complex logic
- Update tests if needed
- Update documentation

### 3. Test Your Changes

```bash
# Run the application
python main.py

# Run tests (if available)
python -m pytest tests/

# Check code style
pylint *.py modules/*.py

# Format code
black *.py modules/*.py
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Type: Brief description"
```

See [Commit Message Guidelines](#commit-message-guidelines) for details.

### 5. Push to Your Fork

```bash
git push origin feature/amazing-feature
```

### 6. Create Pull Request

Go to GitHub and create a pull request from your fork to the main repository.

---

## 🎨 Style Guidelines

### Python Code Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide:

```python
# Good
def calculate_total_xp(notes_count, quizzes_taken):
    """Calculate total XP based on activities."""
    return (notes_count * 10) + (quizzes_taken * 25)

# Bad
def calc_xp(n, q):
    return n*10+q*25
```

### Code Organization

```python
# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
import pandas as pd
from tkinter import messagebox

# Local application imports
from modules import storage
from config import FONT_FAMILY
```

### Naming Conventions

- **Classes**: `PascalCase` - `class NotesManager`
- **Functions/Methods**: `snake_case` - `def get_all_notes()`
- **Constants**: `UPPER_SNAKE_CASE` - `MAX_NOTE_LENGTH = 5000`
- **Private methods**: `_leading_underscore` - `def _validate_input()`
- **Variables**: `snake_case` - `note_count = 0`

### Documentation

Use docstrings for functions, classes, and modules:

```python
def generate_quiz_questions(notes, num_questions=5):
    """
    Generate quiz questions from notes using Gemini AI.
    
    Args:
        notes (list): List of note dictionaries with 'content' key
        num_questions (int): Number of questions to generate (default: 5)
    
    Returns:
        list: List of question-answer dictionaries
        
    Raises:
        ValueError: If notes list is empty
        APIError: If Gemini API call fails
        
    Example:
        >>> notes = [{'content': 'Python is a programming language'}]
        >>> questions = generate_quiz_questions(notes, 3)
        >>> len(questions)
        3
    """
    pass
```

### UI Component Guidelines

```python
# Use descriptive variable names
save_button = ttk.Button(frame, text="Save", command=self.save_note)

# Group related UI elements
def create_header():
    header_frame = ttk.Frame(parent)
    title_label = ttk.Label(header_frame, text="Title")
    # ... more elements
    return header_frame

# Use consistent padding
widget.pack(padx=10, pady=5)
```

---

## 📝 Commit Message Guidelines

### Format

```
Type: Brief description (50 chars or less)

Detailed explanation if needed (wrap at 72 chars).

- Bullet points for multiple changes
- Reference issue numbers: Fixes #123
```

### Types

- **Add**: New feature or functionality
- **Fix**: Bug fix
- **Update**: Update existing feature
- **Refactor**: Code refactoring
- **Docs**: Documentation changes
- **Style**: Code style/formatting changes
- **Test**: Adding or updating tests
- **Chore**: Maintenance tasks

### Examples

```bash
# Good commits
git commit -m "Add: AI-powered quiz generation using Gemini"
git commit -m "Fix: Duplicate notes appearing after deletion"
git commit -m "Update: Increase all font sizes by 3pt"
git commit -m "Docs: Add contributing guidelines"
git commit -m "Refactor: Extract reminder logic to separate module"

# Bad commits
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

---

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated (if applicable)
- [ ] Self-review completed
- [ ] No console.log or debug statements
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Screenshots (if applicable)
Add screenshots

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass
```

### Review Process

1. **Automated checks** - CI/CD runs automatically
2. **Code review** - Maintainer reviews code
3. **Discussion** - Address any feedback
4. **Approval** - Get approval from maintainer
5. **Merge** - PR gets merged

### After Merge

- Delete your branch (if not needed)
- Pull latest changes from main
- Update your fork

```bash
git checkout main
git pull upstream main
git push origin main
```

---

## 🧪 Testing Guidelines

### Writing Tests

```python
def test_note_creation():
    """Test that a new note can be created."""
    note = create_note("Test Title", "Test Content")
    assert note['title'] == "Test Title"
    assert note['content'] == "Test Content"
    assert 'id' in note
    assert 'timestamp' in note
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_storage.py

# Run with coverage
python -m pytest --cov=modules tests/
```

---

## 📚 Additional Resources

### Documentation
- [README.md](README.md) - Project overview
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Code organization
- [CHANGELOG.md](CHANGELOG.md) - Version history

### External Resources
- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Git Best Practices](https://www.git-scm.com/book/en/v2)

---

## ❓ Questions?

- Open an issue with the `question` label
- Join discussions in GitHub Discussions
- Check existing issues and pull requests

---

## 🎉 Recognition

Contributors will be:
- Added to the contributors list
- Mentioned in release notes
- Given credit in documentation

Thank you for contributing! 🚀

---

**Happy Coding! 💻**
