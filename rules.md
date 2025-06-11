# Project Rules and Guidelines

## Code Quality Standards

### Python Code Rules
- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Maximum line length: 88 characters (Black formatter standard)
- Use docstrings for all classes and functions
- Implement proper error handling with specific exception types
- Use logging instead of print statements
- Follow naming conventions: snake_case for variables/functions, PascalCase for classes

### Frontend Code Rules
- Use TypeScript for all new code
- Follow React functional component patterns
- Use proper prop typing with interfaces
- Implement error boundaries for robust error handling
- Use Tailwind CSS classes consistently
- Follow component composition patterns
- Use proper state management (hooks, context)

## Architecture Rules

### Agent Communication
- All inter-agent communication must go through the MCP protocol
- Implement proper message validation and error handling
- Use structured data formats (JSON) for all messages
- Maintain message history for debugging and analysis
- Implement timeouts and retry mechanisms

### Memory Management
- Use the graph database for persistent storage
- Implement proper caching strategies
- Clean up temporary data regularly
- Version control important data changes
- Maintain data consistency across agents

### Error Handling
- Never silence exceptions without proper logging
- Implement graceful degradation for non-critical failures
- Use circuit breaker patterns for external dependencies
- Maintain error context throughout the call stack
- Provide meaningful error messages to users

## Security Rules

### Data Protection
- Never log sensitive information (API keys, passwords, personal data)
- Validate all input data before processing
- Use secure communication channels between components
- Implement proper authentication and authorization
- Sanitize all user inputs

### Code Execution
- Run code execution in sandboxed environments
- Validate code syntax before execution
- Implement resource limits (memory, CPU, time)
- Monitor and log all code execution activities
- Prevent access to restricted system resources

## Performance Rules

### Optimization Guidelines
- Profile code before optimizing
- Use async/await patterns for I/O operations
- Implement proper caching strategies
- Monitor memory usage and prevent leaks
- Use connection pooling for database operations
- Implement proper indexing for frequently queried data

### Resource Management
- Set reasonable timeouts for all operations
- Implement proper connection management
- Use lazy loading for expensive operations
- Monitor system resources and implement alerts
- Clean up resources in finally blocks or context managers

## Testing Rules

### Test Coverage
- Maintain minimum 80% code coverage
- Write unit tests for all business logic
- Implement integration tests for agent communication
- Use mocking for external dependencies
- Test error conditions and edge cases

### Test Organization
- Organize tests by component/module
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Use fixtures for common test data
- Run tests in isolated environments

## Documentation Rules

### Code Documentation
- Document all public APIs
- Include usage examples in docstrings
- Maintain up-to-date README files
- Document configuration options
- Include troubleshooting guides

### Change Management
- Update documentation with code changes
- Maintain changelog for significant updates
- Document breaking changes clearly
- Include migration guides when needed
- Review documentation in code reviews

## Deployment Rules

### Environment Management
- Use environment variables for configuration
- Maintain separate configs for dev/staging/prod
- Implement proper secrets management
- Use container orchestration for scalability
- Monitor application health and performance

### Release Process
- Use semantic versioning
- Tag releases in version control
- Maintain backwards compatibility when possible
- Test thoroughly before production deployment
- Implement rollback procedures

## Monitoring and Logging

### Logging Standards
- Use structured logging (JSON format)
- Include correlation IDs for request tracing
- Log at appropriate levels (DEBUG, INFO, WARN, ERROR)
- Avoid logging sensitive information
- Include relevant context in log messages

### Monitoring Requirements
- Monitor system performance metrics
- Set up alerts for critical failures
- Track business metrics and KPIs
- Implement health checks for all services
- Monitor resource usage and capacity