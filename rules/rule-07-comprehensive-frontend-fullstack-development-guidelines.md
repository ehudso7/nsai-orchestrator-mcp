# Rule #7: Comprehensive Front-End and Full-Stack Development Guidelines

## ReactJS and Modern JavaScript/TypeScript

### Core Principles
- Write clean, efficient, and maintainable React code using modern JavaScript/TypeScript features
- Use functional components with hooks instead of class components
- Prioritize component composition and reusability
- Implement proper state management using React hooks or external libraries
- Follow React best practices and conventions for optimal performance

### React Best Practices
- Use TypeScript for all React projects to ensure type safety
- Prefer functional components with hooks over class components
- Use useState for local component state and useEffect for side effects
- Implement custom hooks for reusable stateful logic
- Use React.memo for performance optimization when necessary
- Apply proper prop validation and default values
- Use lazy loading and code splitting for better performance

### Component Structure
- Create small, focused components with a single responsibility
- Use proper component composition patterns
- Implement error boundaries for robust error handling
- Use context API sparingly for truly global state
- Follow consistent naming conventions (PascalCase for components)
- Organize components in logical folder structures

## Next.js Development

### Core Principles
- Write concise, technical TypeScript code with accurate examples
- Use functional and declarative programming patterns; avoid classes
- Favor iteration and modularization over code duplication
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError)
- Structure files with exported components, subcomponents, helpers, static content, and types
- Use lowercase with dashes for directory names (e.g., components/auth-wizard)

### Next.js Specific Guidelines
- Minimize the use of 'use client', useEffect, and setState; favor React Server Components (RSC)
- Use App Router for new projects and leverage its benefits
- Implement proper SEO optimization with metadata API
- Use Next.js Image component for optimized images
- Leverage automatic static optimization and incremental static regeneration
- Implement proper API routes with TypeScript

### Optimization and Best Practices
- Implement dynamic imports for code splitting and optimization
- Use responsive design with a mobile-first approach
- Optimize images: use WebP format, include size data, implement lazy loading
- Use Next.js built-in performance monitoring and analytics
- Implement proper caching strategies for static and dynamic content

## TypeScript Development

### TypeScript Best Practices
- Use TypeScript for all code; prefer interfaces over types for their extendability
- Avoid enums; use maps instead for better type safety and flexibility
- Use functional components with TypeScript interfaces
- Use the "function" keyword for pure functions to benefit from hoisting and clarity
- Implement strict TypeScript configuration for better type checking
- Use generic types effectively for reusable components

### Type Safety Guidelines
- Define proper types for all function parameters and return values
- Use union types and literal types for better type constraints
- Implement proper error handling with typed exceptions
- Use type guards for runtime type checking
- Create utility types for complex type transformations

## Vue.js and Nuxt Development

### Vue.js Core Principles
- Write concise, maintainable, and technically accurate TypeScript code with relevant examples
- Use functional and declarative programming patterns; avoid classes
- Favor iteration and modularization to adhere to DRY principles and avoid code duplication
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError)
- Organize files systematically: each file should contain only related content

### Vue.js Best Practices
- Always use the Vue Composition API script setup style
- Use Headless UI, Element Plus, and Tailwind for components and styling
- Implement responsive design with Tailwind CSS; use a mobile-first approach
- Use Pinia for state management in Vue 3 applications
- Implement proper component communication with props and events
- Use Vue Router for navigation and route management

### Nuxt 3 Specific Guidelines
- Leverage Nuxt 3's auto-imports and file-based routing
- Use server-side rendering and static site generation appropriately
- Implement proper SEO optimization with useSeoMeta
- Use Nuxt modules for extending functionality
- Implement proper error handling and loading states

## React Native and Mobile Development

### React Native Core Principles
- Write clean, efficient React Native code using TypeScript
- Follow React Native best practices for cross-platform development
- Use platform-specific code when necessary (Platform.OS)
- Implement proper navigation using React Navigation
- Use native modules when performance is critical

### Mobile Development Best Practices
- Design for both iOS and Android platforms
- Implement proper state management using Redux or Context API
- Use AsyncStorage for local data persistence
- Handle network connectivity and offline scenarios
- Implement proper push notification handling
- Use responsive design for different screen sizes

### Expo Development
- Leverage Expo's managed workflow for rapid development
- Use Expo modules for accessing native device features
- Implement proper over-the-air updates with Expo Updates
- Use Expo Application Services (EAS) for building and deployment
- Handle platform differences in Expo environments

## Chrome Extension Development

### Core Principles
- Write clear, modular TypeScript code with proper type definitions
- Follow functional programming patterns; avoid classes
- Strictly follow Manifest V3 specifications
- Divide responsibilities between background, content scripts and popup
- Use chrome.* APIs correctly (storage, tabs, runtime, etc.)

### Chrome Extension Structure
- Implement proper service worker for background functionality
- Use content scripts for DOM manipulation on web pages
- Create intuitive popup interfaces with React or vanilla JS
- Implement proper messaging between different extension contexts
- Use chrome.storage API for persistent data storage

### Security and Performance
- Follow Chrome Web Store policies and guidelines
- Implement proper content security policies (CSP)
- Minimize permissions requested for better user trust
- Optimize extension performance and memory usage
- Handle edge cases and error scenarios gracefully

## Data Analysis with Jupyter and Pandas

### Core Principles
- Write concise, technical responses with accurate Python examples
- Prioritize readability and reproducibility in data analysis workflows
- Use functional programming where appropriate; avoid unnecessary classes
- Prefer vectorized operations over explicit loops for better performance
- Use descriptive variable names that reflect the data they contain
- Follow PEP 8 style guidelines for Python code

### Data Analysis Best Practices
- Use pandas for data manipulation and analysis
- Prefer method chaining for data transformations when possible
- Use loc and iloc for explicit data selection
- Utilize groupby operations for efficient data aggregation
- Implement proper data validation and cleaning procedures
- Use appropriate data types for memory optimization

### Visualization Guidelines
- Use matplotlib for low-level plotting control and customization
- Use seaborn for statistical visualizations and aesthetically pleasing defaults
- Create informative and visually appealing plots with proper labels, titles, and legends
- Use appropriate color schemes and consider color-blindness accessibility
- Implement interactive visualizations with plotly when appropriate

## Python Web Framework Development

### FastAPI Development
- Write asynchronous Python code with proper type hints
- Use Pydantic models for request/response validation
- Implement proper API documentation with OpenAPI/Swagger
- Use dependency injection for shared resources and authentication
- Implement proper error handling and HTTP status codes
- Use FastAPI's built-in security features for authentication

### Django Development
- Follow Django's Model-View-Template (MVT) pattern
- Use Django's ORM effectively for database operations
- Implement proper URL routing and view organization
- Use Django's built-in authentication and authorization
- Follow Django's security best practices
- Use Django Rest Framework for API development

### Flask Development
- Write modular Flask applications with blueprints
- Use Flask extensions for additional functionality
- Implement proper request handling and validation
- Use SQLAlchemy for database operations
- Implement proper error handling and logging
- Follow Flask's application factory pattern for larger applications

## JAX and Machine Learning

### JAX Development Principles
- Write concise, technical Python code with accurate examples
- Prioritize clarity, efficiency, and best practices in deep learning workflows
- Use object-oriented programming for model architectures
- Use functional programming for data processing pipelines
- Implement proper GPU utilization and mixed precision training
- Use descriptive variable names that reflect the components they represent

### Machine Learning Best Practices
- Use JAX's just-in-time compilation for performance optimization
- Implement proper data pipeline with JAX-compatible operations
- Use Flax for neural network implementations
- Implement proper experiment tracking and model checkpointing
- Use proper gradient computation and automatic differentiation
- Handle large datasets with efficient batching strategies

## Web Scraping and Data Extraction

### Core Principles
- Write concise, technical responses with accurate Python examples
- Prioritize readability, efficiency, and maintainability in scraping workflows
- Use modular and reusable functions to handle common scraping tasks
- Handle dynamic and complex websites using appropriate tools
- Follow ethical scraping practices and respect robots.txt

### Web Scraping Tools
- Use requests for simple HTTP GET/POST requests to static websites
- Parse HTML content with BeautifulSoup for efficient data extraction
- Handle JavaScript-heavy websites with selenium or headless browsers
- Use scrapy for large-scale scraping projects
- Implement proper rate limiting and random delays

### Advanced Scraping Techniques
- Use jina or firecrawl for efficient, large-scale text data extraction
- Use agentQL for known, complex processes (e.g., logging in, form submissions)
- Leverage multion for unknown or exploratory tasks
- Handle CAPTCHAs and anti-bot measures appropriately
- Implement proper data validation and storage

## RoboCorp and RPA Development

### RoboCorp Development
- Use Python with Robot Framework for automation tasks
- Implement proper task structure with clear separation of concerns
- Use RoboCorp's cloud platform for deployment and scheduling
- Handle exceptions and error scenarios gracefully
- Implement proper logging and monitoring for automation tasks

### RPA Best Practices
- Design automation workflows that are maintainable and scalable
- Use selectors and element identification strategies that are robust
- Implement proper data handling and validation
- Use version control for automation scripts
- Document automation processes and dependencies clearly

## Python UV Package Management

### UV Package Manager
- Use UV for fast Python package management and environment handling
- Leverage UV's speed advantages over traditional pip and poetry
- Implement proper dependency management with UV
- Use UV for creating and managing virtual environments
- Handle package conflicts and version constraints effectively

### Package Management Best Practices
- Use lock files for reproducible environments
- Implement proper development and production dependency separation
- Use semantic versioning for package releases
- Handle security vulnerabilities in dependencies
- Optimize package installation and caching strategies

## Odoo Development

### Odoo Core Principles
- Write clean Python code following Odoo's coding standards
- Use Odoo's ORM effectively for database operations
- Implement proper module structure and dependencies
- Follow Odoo's security guidelines and access controls
- Use Odoo's built-in features before creating custom solutions

### Odoo Module Development
- Create modular and reusable Odoo addons
- Implement proper data models with appropriate field types
- Use Odoo's view architecture for user interfaces
- Implement proper workflow and business logic
- Handle multi-company and multi-currency scenarios
- Use Odoo's reporting framework for custom reports

## ViewComfy API Integration

### ViewComfy API Development
- Use ViewComfy API for serverless API built using FastAPI framework
- Make requests using the httpx library in Python
- Handle cold starts on first API calls appropriately
- Manage variable generation times effectively
- Ensure params object can't be empty; change seed value if nothing else is specified

### API Integration Best Practices
- Deploy ComfyUI workflow on ViewComfy dashboard using workflow_api.json file
- Create and manage API keys securely from ViewComfy dashboard
- Extract workflow parameters using proper parameter identification
- Use flattened JSON structure for parameter handling
- Handle both standard POST requests and Server-Sent Events for real-time tracking
- Implement proper error handling for API failures and timeouts

## Universal Development Principles

### Code Quality Standards
- Write clean, efficient, well-documented code
- Follow language-specific best practices and conventions
- Create modular, reusable code for flexibility and scalability
- Ensure comprehensive testing strategies and methodologies
- Prioritize security best practices throughout development
- Optimize performance while maintaining code readability

### Error Handling and Validation
- Perform error and edge-case checks at the top of each function (guard clauses)
- Use early returns for invalid inputs and error conditions
- Log errors with structured context (module, function, parameters)
- Raise custom exceptions and map them to user-friendly messages
- Avoid nested conditionals; keep the "happy path" last in the function body

### Performance Optimization
- Minimize file sizes by including only necessary components
- Use CDNs for resources to improve load times and leverage caching
- Optimize images and other assets to enhance overall performance
- Profile code to identify and optimize bottlenecks
- Use appropriate caching strategies and techniques
- Implement proper monitoring and profiling tools

### Security Best Practices
- Implement proper authentication and authorization mechanisms
- Use HTTPS and TLS for secure communication
- Implement input validation and sanitization for all user inputs
- Use proper secrets management and environment variables
- Implement security scanning and vulnerability assessment
- Follow OWASP guidelines and security best practices

### Testing and Quality Assurance
- Follow the Arrange-Act-Assert convention for unit tests
- Name test variables clearly and descriptively
- Write unit tests for each public function and component
- Use test doubles and mocks to simulate dependencies
- Write integration tests for complex workflows
- Follow the Given-When-Then convention for behavior-driven development
- Implement comprehensive testing strategies including end-to-end tests

### Documentation and Maintenance
- Document complex logic and non-obvious code decisions
- Follow official documentation for framework-specific best practices
- Include docstrings for functions, classes, and modules
- Comment on complex or non-obvious code sections
- Maintain API documentation with proper examples
- Include usage examples for public interfaces and components
- Keep documentation up-to-date with code changes

### Development Workflow
- Use version control effectively with meaningful commit messages
- Implement proper branching strategies and code review processes
- Use continuous integration and continuous deployment (CI/CD) practices
- Implement proper dependency management and package handling
- Use linting and formatting tools for consistent code style
- Implement proper environment separation (development, staging, production)

### Cross-Platform Considerations
- Follow API design best practices when applicable
- Maintain consistent coding standards across different projects and platforms
- Implement proper version control and change management strategies
- Use appropriate architectural patterns for each technology domain
- Consider performance implications of implementation choices across platforms
- Ensure proper documentation and code maintainability across team members

## Integration Guidelines

### Multi-Technology Projects
- Design systems that can integrate multiple technologies effectively
- Use appropriate communication protocols between different services
- Implement proper data serialization and deserialization
- Handle different authentication mechanisms across services
- Use appropriate message queuing and event-driven architectures
- Implement proper monitoring and logging across all services

### DevOps and Deployment
- Use containerization with Docker for consistent environments
- Implement proper orchestration with Kubernetes when appropriate
- Use infrastructure as code for reproducible deployments
- Implement proper backup and disaster recovery strategies
- Use monitoring and alerting systems for production environments
- Implement proper scaling strategies for different application components

Refer to official documentation for each technology and framework, and stay updated with the latest best practices, features, and security recommendations for all mentioned technologies.