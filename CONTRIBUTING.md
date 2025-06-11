# Contributing to NSAI Orchestrator MCP

Thank you for your interest in contributing to the NSAI Orchestrator MCP! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Security](#security)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Standards

- Be respectful and inclusive
- Focus on what is best for the community
- Show empathy towards other community members
- Be constructive in discussions and feedback
- Respect different viewpoints and experiences

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Docker and Docker Compose
- Git

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nsai-orchestrator-mcp.git
   cd nsai-orchestrator-mcp
   ```

3. Set up the development environment:
   ```bash
   # Install pre-commit hooks
   pre-commit install
   
   # Create Python virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   pip install -e ".[dev]"
   
   # Install frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

4. Copy environment configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. Start the development environment:
   ```bash
   docker-compose up -d redis neo4j
   python main_enhanced.py
   ```

## Development Workflow

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Examples:
```
feat(agents): add support for custom agent plugins
fix(memory): resolve cache invalidation issue
docs(api): update authentication documentation
```

## Coding Standards

### Python

We follow PEP 8 with these specific guidelines:

- Line length: 127 characters
- Use type hints for all function signatures
- Use docstrings for all public functions and classes
- Format code with `black`
- Lint code with `flake8`
- Type check with `mypy`

Example:
```python
from typing import Dict, Any, Optional


async def process_task(
    task_data: Dict[str, Any],
    agent_type: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a task with the specified agent.
    
    Args:
        task_data: The task configuration and parameters
        agent_type: Type of agent to use for processing
        session_id: Optional session identifier for context
        
    Returns:
        Dict containing the task results and metadata
        
    Raises:
        ValueError: If task_data is invalid
        AgentError: If agent processing fails
    """
    # Implementation here
    pass
```

### TypeScript/React

- Use TypeScript for all new code
- Follow the project's ESLint configuration
- Use functional components with hooks
- Implement proper error handling
- Use React Query for server state management

Example:
```typescript
interface TaskExecutionProps {
  agentType: string;
  taskDescription: string;
  onComplete: (result: TaskResult) => void;
  onError: (error: Error) => void;
}

export function TaskExecution({ 
  agentType, 
  taskDescription, 
  onComplete, 
  onError 
}: TaskExecutionProps) {
  // Implementation here
}
```

### Documentation

- Use clear, concise language
- Include examples for all public APIs
- Update documentation when changing functionality
- Write docstrings for all public functions
- Include type information in docstrings

## Testing

### Test Requirements

All contributions must include appropriate tests:

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete user workflows

### Running Tests

```bash
# Python tests
pytest

# Frontend tests
cd frontend
npm test

# Full test suite
npm run test:all
```

### Test Guidelines

- Write tests before implementing features (TDD)
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Aim for >80% code coverage

Example test:
```python
import pytest
from unittest.mock import AsyncMock

async def test_task_execution_success():
    """Test successful task execution with Claude agent."""
    # Arrange
    mock_agent = AsyncMock()
    mock_agent.execute.return_value = {"status": "completed", "result": "test"}
    
    # Act
    result = await execute_task(mock_agent, {"task": "test task"})
    
    # Assert
    assert result["status"] == "completed"
    assert result["result"] == "test"
    mock_agent.execute.assert_called_once()
```

## Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings and inline comments
2. **API Documentation**: OpenAPI/Swagger specs
3. **User Documentation**: README, guides, tutorials
4. **Developer Documentation**: Contributing guides, architecture docs

### Documentation Guidelines

- Keep documentation up-to-date with code changes
- Use clear, simple language
- Include practical examples
- Provide troubleshooting information
- Link to relevant external resources

## Pull Request Process

### Before Submitting

1. **Run pre-commit checks**:
   ```bash
   pre-commit run --all-files
   ```

2. **Run tests**:
   ```bash
   pytest
   cd frontend && npm test
   ```

3. **Update documentation** if necessary

4. **Test your changes** in a local environment

### PR Submission

1. **Create a clear title** that describes the change
2. **Fill out the PR template** completely
3. **Include screenshots** for UI changes
4. **Reference related issues** using "Fixes #123" or "Relates to #123"
5. **Request review** from appropriate maintainers

### Review Process

1. **Automated checks** must pass (CI/CD, tests, linting)
2. **Code review** by at least one maintainer
3. **Security review** for security-related changes
4. **Documentation review** for public API changes
5. **Final approval** and merge

## Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities. Instead:

1. Email security@nsai.dev with details
2. Include steps to reproduce if possible
3. Allow time for investigation and fixing
4. Coordinate disclosure timeline

### Security Guidelines

- Never commit secrets or credentials
- Use secure coding practices
- Validate all inputs
- Follow authentication and authorization patterns
- Keep dependencies updated

## Plugin Development

### Creating Plugins

1. Use the plugin template:
   ```bash
   mcp-cli plugin create my-plugin --type custom
   ```

2. Follow the plugin architecture guidelines
3. Include comprehensive tests
4. Document plugin capabilities and configuration
5. Submit for review and inclusion in the plugin registry

### Plugin Guidelines

- Implement proper error handling
- Use async/await for I/O operations
- Follow the plugin interface specification
- Include security considerations
- Provide clear documentation

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag the release
- [ ] Build and publish artifacts

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Security Issues**: security@nsai.dev
- **General Contact**: team@nsai.dev

### Resources

- [Documentation](https://docs.nsai.dev)
- [API Reference](https://docs.nsai.dev/api)
- [Plugin Development Guide](https://docs.nsai.dev/plugins)
- [Architecture Overview](https://docs.nsai.dev/architecture)

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation
- Annual contributor spotlight

Thank you for contributing to NSAI Orchestrator MCP! 🚀