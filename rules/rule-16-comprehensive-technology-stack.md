# Rule #11: Comprehensive Technology Stack Guidelines

## JAX and Machine Learning Frameworks

### JAX Development
- Use JAX for high-performance machine learning and scientific computing
- Leverage JAX's just-in-time compilation with `jit` decorator for performance
- Use `grad` for automatic differentiation and `vmap` for vectorization
- Implement pure functions without side effects for JAX transformations
- Use JAX arrays (jnp) instead of NumPy arrays for JAX-compatible operations
- Utilize Flax for neural network layers and Optax for optimization algorithms
- Use JAX's PRNG system with explicit key splitting for reproducible randomness

### Advanced JAX Patterns
- Use `pmap` for multi-device parallelization across GPUs/TPUs
- Implement custom derivatives with `custom_vjp` and `custom_jvp`
- Use JAX's experimental features like `scan` and `while_loop` for efficient loops
- Leverage JAX-MD for molecular dynamics simulations
- Use Haiku for neural network building with JAX

## Web Scraping and Data Extraction

### Python Web Scraping
- Use requests-html, playwright, or selenium for dynamic content
- Implement proper rate limiting and respect robots.txt
- Use rotating proxies and user agents to avoid detection
- Handle JavaScript-rendered content with headless browsers
- Use BeautifulSoup or lxml for HTML parsing
- Implement retry mechanisms with exponential backoff
- Use async/await with aiohttp for concurrent scraping

### Web Scraping Best Practices
- Cache responses to avoid redundant requests
- Use session management for maintaining state
- Implement proper error handling for network failures
- Store data in structured formats (JSON, CSV, databases)
- Use data validation and cleaning pipelines
- Respect website terms of service and legal considerations

## RoboCorp and RPA Development

### RoboCorp Framework
- Use Robot Framework syntax for automation scripts
- Implement proper library imports and resource files
- Use RoboCorp Cloud for robot deployment and management
- Implement error handling with Try-Except-Finally blocks
- Use variables and arguments for flexible automation
- Implement logging and reporting for debugging

### RPA Best Practices
- Design modular robots with reusable keywords
- Use page object model for web automation
- Implement proper wait strategies for element loading
- Use data-driven testing with external data sources
- Implement proper exception handling and recovery
- Use version control for robot development

## Python Package Management with UV

### UV Package Manager
- Use `uv` exclusively for Python dependency management
- Commands:
  - `uv add <package>` - Add dependencies
  - `uv remove <package>` - Remove dependencies
  - `uv sync` - Sync dependencies from lock file
  - `uv run <script>` - Run scripts with proper environment
  - `uv venv` - Create virtual environments
  - `uv pip` - Use pip-compatible interface when needed

### UV Workflow Best Practices
- Always commit `uv.lock` file to version control
- Use `uv.toml` for project configuration
- Separate development and production dependencies
- Use dependency groups for optional features
- Regular dependency updates with `uv update`

## Odoo Development Advanced Guidelines

### Odoo Architecture Patterns
- Implement proper MVC architecture with models, views, controllers
- Use Odoo's ORM methods efficiently (create, write, search, browse)
- Implement proper inheritance patterns (classical, delegation, extension)
- Use computed fields with proper dependencies (@api.depends)
- Implement onchange methods for dynamic form behavior

### Odoo Security and Performance
- Implement proper access control with security rules
- Use record rules for row-level security
- Optimize database queries with proper domain filters
- Use Odoo's caching mechanisms effectively
- Implement proper transaction management
- Use background jobs for long-running operations

### Odoo Module Development
- Follow Odoo's module structure conventions
- Implement proper manifest files (__manifest__.py)
- Use XML for view definitions and data files
- Implement proper translation support with .po files
- Use Odoo's testing framework for unit and integration tests
- Follow PEP 8 and Odoo coding standards

## ViewComfy API Integration

### ViewComfy Workflow Development
- Use ComfyUI API for image generation workflows
- Implement proper node connections and data flow
- Use checkpoint loaders and model management
- Implement proper prompt handling and conditioning
- Use ControlNet and other conditioning methods
- Handle different image formats and resolutions

### ViewComfy Best Practices
- Implement error handling for API failures
- Use proper queue management for batch processing
- Implement progress tracking for long-running workflows
- Use proper image preprocessing and postprocessing
- Handle memory management for large workflows
- Implement proper logging and debugging

## Additional Technology Guidelines

### FastAPI Advanced Patterns
- Use dependency injection for database connections and services
- Implement proper authentication with JWT tokens
- Use Pydantic models for request/response validation
- Implement proper error handling with custom exception handlers
- Use background tasks for asynchronous operations
- Implement proper CORS and security headers

### Database Management
- Use SQLAlchemy ORM with proper model definitions
- Implement database migrations with Alembic
- Use connection pooling for production environments
- Implement proper indexing for query optimization
- Use database constraints for data integrity
- Implement proper backup and recovery strategies

### API Development Best Practices
- Follow RESTful API design principles
- Use proper HTTP status codes and error responses
- Implement API versioning strategies
- Use proper pagination for large datasets
- Implement rate limiting and throttling
- Use API documentation with OpenAPI/Swagger

### Docker and Containerization
- Write efficient Dockerfiles with multi-stage builds
- Use proper base images and security scanning
- Implement proper volume management for data persistence
- Use docker-compose for multi-service applications
- Implement proper networking and service discovery
- Use proper logging and monitoring in containers

### Kubernetes and Orchestration
- Use Kubernetes manifests for application deployment
- Implement proper resource limits and requests
- Use ConfigMaps and Secrets for configuration management
- Implement proper health checks and readiness probes
- Use ingress controllers for external access
- Implement proper monitoring and logging

### Cloud Development (AWS/Azure/GCP)
- Use infrastructure as code (Terraform, CloudFormation)
- Implement proper IAM and security policies
- Use managed services for databases and messaging
- Implement proper monitoring and alerting
- Use auto-scaling and load balancing
- Implement disaster recovery and backup strategies

### Microservices Architecture
- Design services with single responsibility principle
- Use event-driven architecture for service communication
- Implement proper service discovery and load balancing
- Use circuit breakers for fault tolerance
- Implement distributed tracing and monitoring
- Use API gateways for external communication

### Testing Strategies
- Implement unit tests with proper mocking
- Use integration tests for API endpoints
- Implement end-to-end tests for critical workflows
- Use test fixtures and factories for test data
- Implement proper test coverage measurement
- Use continuous integration for automated testing

### Security Best Practices
- Implement proper authentication and authorization
- Use HTTPS and TLS for secure communication
- Implement input validation and sanitization
- Use proper secrets management
- Implement security scanning and vulnerability assessment
- Follow OWASP security guidelines

### Performance Optimization
- Use proper caching strategies (Redis, Memcached)
- Implement database query optimization
- Use CDNs for static content delivery
- Implement proper monitoring and profiling
- Use async programming for I/O-bound operations
- Implement proper resource management

### Data Engineering
- Use ETL/ELT pipelines for data processing
- Implement proper data validation and quality checks
- Use data warehousing and data lakes for storage
- Implement proper data lineage and governance
- Use streaming data processing (Kafka, Pulsar)
- Implement proper data backup and recovery

### DevOps and CI/CD
- Use version control best practices (Git)
- Implement proper branching strategies
- Use automated testing in CI/CD pipelines
- Implement proper deployment strategies (blue-green, canary)
- Use infrastructure monitoring and alerting
- Implement proper rollback and disaster recovery

## Universal Development Principles

### Code Quality Standards
- Write clean, maintainable, and well-documented code
- Follow language-specific style guides and conventions
- Use static code analysis and linting tools
- Implement proper error handling and logging
- Use design patterns and architectural principles
- Regular code reviews and pair programming

### Project Management
- Use agile development methodologies
- Implement proper requirements gathering and analysis
- Use project tracking and management tools
- Implement proper risk management and mitigation
- Use proper documentation and knowledge management
- Regular stakeholder communication and feedback

### Continuous Learning
- Stay updated with latest technology trends
- Participate in open source projects
- Attend conferences and workshops
- Read technical blogs and documentation
- Practice with personal projects and experiments
- Share knowledge through teaching and mentoring