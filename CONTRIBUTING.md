# 🤝 Contributing to Lead Generation Tool

Thank you for your interest in contributing to the Lead Generation Tool! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## 🤗 Code of Conduct

This project follows a Code of Conduct to ensure a welcoming and inclusive environment for all contributors.

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:
- Python 3.11 or higher
- Git
- A GitHub account
- Basic knowledge of Flask and REST APIs

### First Steps

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/lead-generation-tool.git
   cd lead-generation-tool
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/femydatagent/lead-generation-tool.git
   ```

## 💻 Development Setup

### 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Required
SERPAPI_API_KEY=your_serpapi_key

# Optional
DATASTONE_API_TOKEN=your_datastone_token
APIFY_API_TOKEN=your_apify_token

# Supabase (if testing with Supabase backend)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
```

### 4. Run the Application

```bash
python src/main.py
```

The application will be available at `http://localhost:5000`

### 5. Test API Connectivity

```bash
python test_apis.py
```

## 📁 Project Structure

```
lead-generation-tool/
├── src/                          # Main application code
│   ├── main.py                  # Flask app initialization
│   ├── routes/                  # API route handlers
│   │   ├── leads_smart.py       # Smart lead generation with AI
│   │   ├── leads_simple.py      # Simple lead generation
│   │   └── user.py              # User management
│   ├── models/                  # Database models
│   │   └── user.py              # User model
│   ├── static/                  # Frontend files
│   │   └── index.html           # Web interface
│   └── database/                # SQLite database
│
├── supabase/                    # Supabase backend
│   ├── schema.sql              # Database schema
│   ├── functions/              # Edge Functions
│   └── config.toml             # Supabase configuration
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── test_apis.py               # API testing utility
└── deploy_backend.py          # Deployment script
```

## 📝 Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) style guide:

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 120 characters
- **Naming Conventions**:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

### Code Quality

- Write clear, self-documenting code
- Add comments for complex logic
- Use type hints where appropriate
- Keep functions small and focused (single responsibility)

### Example:

```python
def calcular_similaridade(texto1: str, texto2: str) -> float:
    """
    Calculate similarity ratio between two texts.

    Args:
        texto1: First text to compare
        texto2: Second text to compare

    Returns:
        float: Similarity ratio between 0.0 and 1.0
    """
    texto1_norm = normalizar_texto(texto1)
    texto2_norm = normalizar_texto(texto2)
    return SequenceMatcher(None, texto1_norm, texto2_norm).ratio()
```

### Documentation

- Add docstrings to all functions and classes
- Use Google-style or NumPy-style docstrings
- Document API endpoints with request/response examples
- Update README when adding features

## 🧪 Testing

### Manual Testing

1. **Test the Web Interface**:
   - Navigate to `http://localhost:5000`
   - Try generating leads with different parameters
   - Verify CSV download works

2. **Test API Endpoints**:
   ```bash
   # Start lead generation
   curl -X POST http://localhost:5000/api/leads/generate \
     -H "Content-Type: application/json" \
     -d '{"tipo_negocio": "restaurante", "localizacao": "São Paulo, SP"}'

   # Check status
   curl http://localhost:5000/api/leads/status/JOB_ID
   ```

### Testing Checklist

Before submitting a PR, verify:
- [ ] Code runs without errors
- [ ] API endpoints return expected responses
- [ ] Frontend displays data correctly
- [ ] CSV export works properly
- [ ] Error handling works as expected
- [ ] Code follows style guidelines
- [ ] Documentation is updated

## 📤 Submitting Changes

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/instagram-scraping-improvement`
- `fix/cnpj-validation-bug`
- `docs/api-documentation`

### 2. Make Your Changes

- Write clean, well-documented code
- Follow coding standards
- Test your changes thoroughly
- Commit often with clear messages

### 3. Commit Guidelines

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "Add confidence scoring for Instagram extraction"
git commit -m "Fix CNPJ regex pattern validation"
git commit -m "Update API documentation with new endpoints"

# Bad examples
git commit -m "fix bug"
git commit -m "update"
git commit -m "changes"
```

**Commit Message Format**:
```
<type>: <subject>

<body>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 4. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 5. Create a Pull Request

1. Go to the [original repository](https://github.com/femydatagent/lead-generation-tool)
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template:
   - **Title**: Clear, concise description
   - **Description**: What changes were made and why
   - **Related Issues**: Link to any related issues
   - **Testing**: How you tested the changes

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commits are clean and well-described
- [ ] No unnecessary files included
- [ ] Branch is up-to-date with main

## 🐛 Reporting Bugs

### Before Reporting

1. Check if the bug has already been reported in [Issues](https://github.com/femydatagent/lead-generation-tool/issues)
2. Try to reproduce the bug with the latest version
3. Gather as much information as possible

### Bug Report Template

```markdown
## Bug Description
Clear description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.11.5]
- Browser: [e.g., Chrome 120]

## Additional Context
- Error messages
- Screenshots
- Logs
```

## 💡 Feature Requests

We welcome feature suggestions! To request a feature:

1. **Check existing requests** in [Issues](https://github.com/femydatagent/lead-generation-tool/issues)
2. **Create a new issue** with the label "enhancement"
3. **Describe the feature**:
   - What problem does it solve?
   - How would it work?
   - Why is it valuable?
4. **Provide examples** if applicable

## 🔍 Code Review Process

All contributions go through code review:

1. **Automated Checks**: Linting, formatting
2. **Manual Review**: Code quality, logic, documentation
3. **Testing**: Functionality verification
4. **Feedback**: Constructive suggestions for improvement

**Timeline**: Reviews typically happen within 2-5 business days.

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com)
- [SerpApi Documentation](https://serpapi.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Python Best Practices](https://docs.python-guide.org)

## ❓ Questions?

If you have questions:
- Open a [Discussion](https://github.com/femydatagent/lead-generation-tool/discussions)
- Ask in an [Issue](https://github.com/femydatagent/lead-generation-tool/issues)
- Contact the maintainers

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Happy Contributing!** 🎉
