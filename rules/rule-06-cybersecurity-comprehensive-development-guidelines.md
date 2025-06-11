# Rule #6: Cybersecurity and Comprehensive Development Guidelines

## Python Cybersecurity Tool Development

### Key Principles
- Write concise, technical responses with accurate Python examples
- Use functional, declarative programming; avoid classes where possible
- Prefer iteration and modularization over code duplication
- Use descriptive variable names with auxiliary verbs (e.g., is_encrypted, has_valid_signature)
- Use lowercase with underscores for directories and files (e.g., scanners/port_scanner.py)
- Favor named exports for commands and utility functions
- Follow the Receive an Object, Return an Object (RORO) pattern for all tool interfaces

### Python/Cybersecurity Structure
- Use `def` for pure, CPU-bound routines; `async def` for network- or I/O-bound operations
- Add type hints for all function signatures; validate inputs with Pydantic v2 models where structured config is required
- Organize file structure into modules:
  - `scanners/` (port, vulnerability, web)
  - `enumerators/` (dns, smb, ssh)
  - `attackers/` (brute_forcers, exploiters)
  - `reporting/` (console, HTML, JSON)
  - `utils/` (crypto_helpers, network_helpers)
  - `types/` (models, schemas)

### Security-Specific Guidelines
- Sanitize all external inputs; never invoke shell commands with unsanitized strings
- Use secure defaults (e.g., TLSv1.2+, strong cipher suites)
- Implement rate-limiting and back-off for network scans to avoid detection and abuse
- Ensure secrets (API keys, credentials) are loaded from secure stores or environment variables
- Provide both CLI and RESTful API interfaces using the RORO pattern for tool control
- Use middleware (or decorators) for centralized logging, metrics, and exception handling

### Performance Optimization
- Utilize asyncio and connection pooling for high-throughput scanning or enumeration
- Batch or chunk large target lists to manage resource utilization
- Cache DNS lookups and vulnerability database queries when appropriate
- Lazy-load heavy modules (e.g., exploit databases) only when needed

## Laravel Development

### Laravel with Livewire and DaisyUI
- Write concise, technical responses with accurate PHP and Livewire examples
- Focus on component-based architecture using Livewire and Laravel's latest features
- Follow Laravel and Livewire best practices and conventions
- Use object-oriented programming with a focus on SOLID principles
- Prefer iteration and modularization over duplication
- Use descriptive variable, method, and component names

### Laravel with Vue.js
- Write concise, technical responses with accurate examples in PHP and Vue.js
- Follow Laravel and Vue.js best practices and conventions
- Use object-oriented programming with a focus on SOLID principles
- Favor iteration and modularization over duplication
- Use descriptive and meaningful names for variables, methods, and files
- Adhere to Laravel's directory structure conventions
- Prioritize dependency injection and service containers

### PHP/Laravel Best Practices
- Use PHP 8.1+ features when appropriate (e.g., typed properties, match expressions)
- Follow PSR-12 coding standards
- Use strict typing: `declare(strict_types=1);`
- Utilize Laravel 11's built-in features and helpers when possible
- Implement proper error handling and logging
- Use Laravel's validation features for form and request validation
- Implement middleware for request filtering and modification
- Utilize Laravel's Eloquent ORM for database interactions

### Livewire Specific Guidelines
- Use Livewire for dynamic components and real-time user interactions
- Favor the use of Livewire's lifecycle hooks and properties
- Use the latest Livewire (3.5+) features for optimization and reactivity
- Implement Blade components with Livewire directives (e.g., wire:model)
- Handle state management and form handling using Livewire properties and actions
- Use wire:loading and wire:target to provide feedback and optimize user experience

## Vue.js Development

### TypeScript, Node.js, Vite, Vue.js Stack
- Write concise, maintainable, and technically accurate TypeScript code with relevant examples
- Use functional and declarative programming patterns; avoid classes
- Favor iteration and modularization to adhere to DRY principles and avoid code duplication
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError)
- Organize files systematically: each file should contain only related content

### Vue.js Best Practices
- Use TypeScript for all code; prefer interfaces over types for their extendability
- Avoid enums; use maps instead for better type safety and flexibility
- Use functional components with TypeScript interfaces
- Use the "function" keyword for pure functions to benefit from hoisting and clarity
- Always use the Vue Composition API script setup style
- Use Headless UI, Element Plus, and Tailwind for components and styling
- Implement responsive design with Tailwind CSS; use a mobile-first approach

## WordPress Development

### Core Principles
- Write concise, technical responses with accurate PHP examples
- Follow WordPress coding standards and best practices
- Use object-oriented programming when appropriate, focusing on modularity
- Prefer iteration and modularization over duplication
- Use descriptive function, variable, and file names
- Use lowercase with hyphens for directories (e.g., wp-content/themes/my-theme)
- Favor hooks (actions and filters) for extending functionality

### WordPress Best Practices
- Use WordPress hooks (actions and filters) instead of modifying core files
- Implement proper theme functions using functions.php
- Use WordPress's built-in user roles and capabilities system
- Utilize WordPress's transients API for caching
- Implement background processing for long-running tasks using wp_cron()
- Use WordPress's built-in testing tools (WP_UnitTestCase) for unit tests
- Implement proper internationalization and localization using WordPress i18n functions

## Ghost CMS Development

### Key Principles
- Write concise, technical responses with accurate Ghost theme examples
- Leverage Ghost's content API and dynamic routing effectively
- Prioritize performance optimization and proper asset management
- Use descriptive variable names and follow Ghost's naming conventions
- Organize files using Ghost's theme structure

### Ghost Theme Structure
- Use the recommended Ghost theme structure:
  - assets/ (css/, js/, images/)
  - partials/
  - post.hbs, page.hbs, index.hbs, default.hbs
  - package.json

### Component Development
- Create .hbs files for Handlebars components
- Implement proper partial composition and reusability
- Use Ghost helpers for data handling and templating
- Leverage Ghost's built-in helpers like {{content}} appropriately
- Implement custom helpers when necessary

## Drupal 10 Module Development

### Core Principles
- Write concise, technically accurate PHP code with proper Drupal API examples
- Follow SOLID principles for object-oriented programming
- Write maintainable code that follows the DRY principle
- Adhere to Drupal coding standards and best practices
- Design for maintainability and integration with other Drupal modules
- Use consistent naming conventions that follow Drupal patterns
- Leverage Drupal's service container and plugin system

### PHP Standards
- Use PHP 8.1+ features when appropriate (typed properties, match expressions, etc.)
- Follow Drupal's PHP coding standards (based on PSR-12 with modifications)
- Always use strict typing: `declare(strict_types=1);`
- Implement proper error handling with try-catch blocks and Drupal's logging system
- Use type hints for method parameters and return types

### Drupal Best Practices
- Use Drupal's database API instead of raw SQL queries
- Implement the Repository pattern for data access logic
- Utilize Drupal's service container for dependency injection
- Leverage Drupal's caching API for performance optimization
- Use Drupal's Queue API for background processing
- Implement comprehensive testing using PHPUnit and Drupal's testing framework

## Next.js Development

### Core Principles
- Write concise, technical TypeScript code with accurate examples
- Use functional and declarative programming patterns; avoid classes
- Favor iteration and modularization over code duplication
- Use descriptive variable names with auxiliary verbs (e.g., `isLoading`, `hasError`)
- Structure files with exported components, subcomponents, helpers, static content, and types
- Use lowercase with dashes for directory names (e.g., `components/auth-wizard`)

### Optimization and Best Practices
- Minimize the use of `'use client'`, `useEffect`, and `setState`; favor React Server Components (RSC)
- Implement dynamic imports for code splitting and optimization
- Use responsive design with a mobile-first approach
- Optimize images: use WebP format, include size data, implement lazy loading

### Error Handling and Validation
- Prioritize error handling and edge cases
- Use early returns for error conditions
- Implement guard clauses to handle preconditions and invalid states early
- Use custom error types for consistent error handling

## Go API Development

### Key Principles
- Follow RESTful API design principles, best practices, and Go idioms
- Use the standard library's net/http package for API development
- Utilize the new ServeMux introduced in Go 1.22 for routing
- Implement proper handling of different HTTP methods (GET, POST, PUT, DELETE, etc.)
- Use method handlers with appropriate signatures
- Leverage new features like wildcard matching and regex support in routes

### Implementation Guidelines
- Implement proper error handling, including custom error types when beneficial
- Use appropriate status codes and format JSON responses correctly
- Implement input validation for API endpoints
- Utilize Go's built-in concurrency features when beneficial for API performance
- Include necessary imports, package declarations, and any required setup code
- Implement proper logging using the standard library's log package

## Data Analysis and Jupyter Development

### Key Principles
- Write concise, technical responses with accurate Python examples
- Prioritize readability and reproducibility in data analysis workflows
- Use functional programming where appropriate; avoid unnecessary classes
- Prefer vectorized operations over explicit loops for better performance
- Use descriptive variable names that reflect the data they contain
- Follow PEP 8 style guidelines for Python code

### Data Analysis and Manipulation
- Use pandas for data manipulation and analysis
- Prefer method chaining for data transformations when possible
- Use loc and iloc for explicit data selection
- Utilize groupby operations for efficient data aggregation

### Visualization
- Use matplotlib for low-level plotting control and customization
- Use seaborn for statistical visualizations and aesthetically pleasing defaults
- Create informative and visually appealing plots with proper labels, titles, and legends
- Use appropriate color schemes and consider color-blindness accessibility

## Bootstrap and Modern Web Development

### Key Principles
- Write clear, concise, and technical responses with precise Bootstrap examples
- Utilize Bootstrap's components and utilities to streamline development and ensure responsiveness
- Prioritize maintainability and readability; adhere to clean coding practices
- Use descriptive class names and structure to promote clarity and collaboration

### Bootstrap Usage
- Leverage Bootstrap's grid system for responsive layouts
- Utilize Bootstrap components (e.g., buttons, modals, alerts) to enhance user experience
- Apply Bootstrap's utility classes for quick styling adjustments
- Ensure all components are accessible; use ARIA attributes and semantic HTML where applicable

## HTMX Development

### Key Principles
- Write concise, clear, and technical responses with precise HTMX examples
- Utilize HTMX's capabilities to enhance the interactivity of web applications without heavy JavaScript
- Prioritize maintainability and readability; adhere to clean coding practices
- Use descriptive attribute names in HTMX for better understanding and collaboration

### HTMX Usage
- Use hx-get, hx-post, and other HTMX attributes to define server requests directly in HTML
- Structure responses from the server to return only necessary HTML snippets
- Favor declarative attributes over JavaScript event handlers
- Leverage hx-trigger to customize event handling and control when requests are sent
- Utilize hx-target to specify where the response content should be injected in the DOM

## Java Development

### Spring Boot Development
- Write clean, efficient, and well-documented Java code with accurate Spring Boot examples
- Use Spring Boot best practices and conventions throughout your code
- Implement RESTful API design patterns when creating web services
- Use descriptive method and variable names following camelCase convention
- Structure Spring Boot applications: controllers, services, repositories, models, configurations

### Quarkus Framework Development
- Write clean, efficient, and well-documented Java code using Quarkus best practices
- Follow Jakarta EE and MicroProfile conventions, ensuring clarity in package organization
- Use descriptive method and variable names following camelCase convention
- Structure your application with consistent organization
- Leverage Quarkus Dev Mode for faster development cycles
- Use Quarkus annotations effectively
- Implement build-time optimizations using Quarkus extensions and best practices

### Java Best Practices
- Use Java 17 or later features when applicable (e.g., records, sealed classes, pattern matching)
- Leverage modern Java frameworks' features and best practices
- Use appropriate data access technologies for database operations
- Implement proper validation using Bean Validation
- Use constructor injection over field injection for better testability
- Leverage dependency injection containers for managing bean lifecycles

## .NET Development

### Core Principles
- Write concise, idiomatic C# code with accurate examples
- Follow .NET and ASP.NET Core conventions and best practices
- Use object-oriented and functional programming patterns as appropriate
- Prefer LINQ and lambda expressions for collection operations
- Use descriptive variable and method names
- Structure files according to .NET conventions

### C# and .NET Usage
- Use C# 10+ features when appropriate (e.g., record types, pattern matching, null-coalescing assignment)
- Leverage built-in ASP.NET Core features and middleware
- Use Entity Framework Core effectively for database operations
- Follow the C# Coding Conventions
- Use C#'s expressive syntax (e.g., null-conditional operators, string interpolation)

### Blazor Development
- Write idiomatic and efficient Blazor and C# code
- Follow .NET and Blazor conventions
- Use Razor Components appropriately for component-based UI development
- Prefer inline functions for smaller components but separate complex logic into code-behind or service classes
- Async/await should be used where applicable to ensure non-blocking UI operations

## Unity Game Development

### Key Principles
- Write clear, technical responses with precise C# and Unity examples
- Use Unity's built-in features and tools wherever possible to leverage its full capabilities
- Prioritize readability and maintainability; follow C# coding conventions and Unity best practices
- Use descriptive variable and function names; adhere to naming conventions
- Structure your project in a modular way using Unity's component-based architecture

### C#/Unity Best Practices
- Use MonoBehaviour for script components attached to GameObjects
- Prefer ScriptableObjects for data containers and shared resources
- Leverage Unity's physics engine and collision detection system for game mechanics and interactions
- Use Unity's Input System for handling player input across multiple platforms
- Utilize Unity's UI system (Canvas, UI elements) for creating user interfaces
- Follow the Component pattern strictly for clear separation of concerns and modularity

## TypeScript and NestJS Development

### TypeScript General Guidelines
- Use English for all code and documentation
- Always declare the type of each variable and function (parameters and return value)
- Avoid using any; create necessary types
- Use JSDoc to document public classes and methods
- Don't leave blank lines within a function
- One export per file

### NestJS Specific Guidelines
- Use modular architecture
- Encapsulate the API in modules
- One module per main domain/route
- One controller for its route
- A models folder with data types
- DTOs validated with class-validator for inputs
- A services module with business logic and persistence
- A core module for nest artifacts
- A shared module for services shared between modules

## ViewComfy API Integration

### ViewComfy API Development
- Use ViewComfy API for serverless API built using FastAPI framework that can run custom ComfyUI workflows
- Make requests using the httpx library in Python
- Handle cold starts on first API calls
- Manage variable generation times (some might be less than 2 seconds, others several minutes)
- Ensure params object can't be empty; change seed value if nothing else is specified

### API Response Format
- Handle responses with following format:
  - prompt_id: Unique identifier for the prompt
  - status: Current execution status
  - completed: Whether execution is complete
  - execution_time_seconds: Time taken to execute
  - prompt: Original prompt configuration
  - outputs: List of output files with filename, content_type, data (base64), and size

### ViewComfy Best Practices
- Deploy ComfyUI workflow on ViewComfy dashboard using workflow_api.json file
- Create API keys from ViewComfy dashboard
- Extract workflow parameters using workflow_parameters_maker.py
- Use flattened JSON structure for parameter identification
- Handle both standard POST requests and Server-Sent Events for real-time tracking
- Implement proper error handling for API failures and timeouts

## Universal Development Principles

### Error Handling and Validation
- Perform error and edge-case checks at the top of each function (guard clauses)
- Use early returns for invalid inputs (e.g., malformed target addresses)
- Log errors with structured context (module, function, parameters)
- Raise custom exceptions and map them to user-friendly CLI/API messages
- Avoid nested conditionals; keep the "happy path" last in the function body

### Performance Optimization
- Minimize file sizes by including only necessary components
- Use CDNs for resources to improve load times and leverage caching
- Optimize images and other assets to enhance overall performance
- Profile code to identify and optimize bottlenecks
- Use appropriate caching strategies

### Security Best Practices
- Implement proper authentication and authorization
- Use HTTPS and TLS for secure communication
- Implement input validation and sanitization
- Use proper secrets management
- Implement security scanning and vulnerability assessment
- Follow security guidelines and best practices

### Testing and Quality Assurance
- Follow the Arrange-Act-Assert convention for tests
- Name test variables clearly
- Write unit tests for each public function
- Use test doubles to simulate dependencies
- Write acceptance tests for each module
- Follow the Given-When-Then convention
- Implement comprehensive testing strategies

### Key Conventions
1. Rely on dependency injection for shared resources
2. Prioritize measurable security metrics
3. Avoid blocking operations in core loops; extract heavy I/O to dedicated async helpers
4. Use structured logging (JSON) for easy ingestion by SIEMs
5. Automate testing of edge cases with appropriate testing frameworks
6. Follow official documentation for each technology
7. Stay updated with latest best practices and features
8. Implement proper error handling and logging consistently across applications

### Documentation and Maintenance
- Document complex logic and non-obvious code decisions
- Follow official documentation for best practices
- Include docstrings for functions and modules
- Comment on complex or non-obvious code sections
- Maintain API documentation
- Include usage examples for public interfaces

Refer to OWASP Testing Guide, NIST SP 800-115, FastAPI docs, and respective technology documentation for best practices in each domain.