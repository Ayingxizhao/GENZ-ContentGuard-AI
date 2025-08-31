# Contributing to ContentGuard AI

Thank you for your interest in contributing to ContentGuard AI! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the GitHub issue tracker to report bugs or suggest features
- Provide detailed information about the issue
- Include steps to reproduce the problem
- Mention your operating system and Python version

### Submitting Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🛠️ Development Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Local Development
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/contentguard-ai.git
   cd contentguard-ai
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. Run tests
   ```bash
   pytest
   ```

## 📝 Code Style

### Python
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused

### JavaScript
- Use ES6+ features
- Follow consistent indentation
- Add comments for complex logic

### CSS
- Use consistent naming conventions
- Organize styles logically
- Use meaningful class names

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=./ --cov-report=html

# Run specific test file
pytest tests/test_model.py
```

### Writing Tests
- Write tests for new functionality
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

## 📚 Documentation

### Code Documentation
- Add docstrings to all functions and classes
- Use clear and concise language
- Include examples where helpful

### README Updates
- Update README.md for new features
- Include usage examples
- Update installation instructions if needed

## 🔒 Security

### Reporting Security Issues
- Do not report security issues in public GitHub issues
- Email security issues to: security@contentguard-ai.com
- Include detailed information about the vulnerability

### Security Guidelines
- Never commit sensitive information (API keys, passwords)
- Use environment variables for configuration
- Validate all user inputs
- Follow secure coding practices

## 🏷️ Commit Messages

Use clear and descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

Example:
```
Add user authentication system

- Implement JWT token-based authentication
- Add login and logout endpoints
- Include password hashing with bcrypt
- Add user registration functionality

Fixes #123
```

## 📋 Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows style guidelines
- [ ] Tests pass and new tests are added
- [ ] Documentation is updated
- [ ] No sensitive information is included
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up to date with main

## 🎯 Areas for Contribution

### High Priority
- Bug fixes and performance improvements
- Enhanced machine learning models
- Better error handling and user feedback
- Additional language support

### Medium Priority
- UI/UX improvements
- Additional analysis features
- Documentation improvements
- Test coverage expansion

### Low Priority
- Code refactoring
- Minor feature additions
- Documentation updates

## 📞 Getting Help

If you need help with contributing:
- Check existing issues and pull requests
- Join our community discussions
- Contact the maintainers

## 🙏 Recognition

Contributors will be recognized in:
- The project README
- Release notes
- Contributor hall of fame

Thank you for contributing to ContentGuard AI! 🛡️
