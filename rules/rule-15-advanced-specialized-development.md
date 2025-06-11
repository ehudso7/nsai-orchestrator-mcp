# Rule #10: Advanced Specialized Development Guidelines

## Deep Learning and AI Development

### PyTorch, Transformers, and Diffusion Models
- Use PyTorch as the primary framework for deep learning tasks
- Implement custom nn.Module classes for model architectures
- Utilize PyTorch's autograd for automatic differentiation
- Use the Transformers library for working with pre-trained models and tokenizers
- Implement attention mechanisms and positional encodings correctly
- Use Diffusers library for implementing diffusion models
- Understand forward and reverse diffusion processes
- Implement proper StableDiffusionPipeline and StableDiffusionXLPipeline

### Model Training and Evaluation
- Implement efficient data loading using PyTorch's DataLoader
- Use proper train/validation/test splits and cross-validation
- Implement early stopping and learning rate scheduling
- Use appropriate evaluation metrics for specific tasks
- Implement gradient clipping and proper handling of NaN/Inf values
- Utilize DataParallel or DistributedDataParallel for multi-GPU training
- Use mixed precision training with torch.cuda.amp

### Gradio Integration
- Create interactive demos using Gradio for model inference and visualization
- Design user-friendly interfaces that showcase model capabilities
- Implement proper error handling and input validation in Gradio apps

## DevOps and Cloud Engineering

### Azure and Kubernetes
- Use YAML pipelines for modular and reusable configurations
- Include stages for build, test, security scans, and deployment
- Ensure secure pod-to-service communications using Kubernetes-native tools
- Use HPA (Horizontal Pod Autoscaler) for scaling applications
- Implement network policies to restrict traffic flow

### Bash and Ansible Automation
- Use descriptive names for scripts and variables
- Write modular scripts with functions for readability and reuse
- Follow idempotent design principles for all playbooks
- Use Ansible Vault to manage sensitive information
- Use dynamic inventories for cloud environments

### System Design Principles
- Design solutions for high availability and fault tolerance
- Use event-driven architecture with tools like Azure Event Grid or Kafka
- Optimize for performance by analyzing bottlenecks
- Secure systems using TLS, IAM roles, and firewalls

## Java and Enterprise Development

### Quarkus Framework
- Leverage Quarkus Dev Mode for faster development cycles
- Use Quarkus annotations (@ApplicationScoped, @Inject, @ConfigProperty)
- Implement build-time optimizations using Quarkus extensions
- Configure native builds with GraalVM for optimal performance
- Use CDI annotations for clean and testable code
- Implement reactive patterns with Vert.x or Mutiny for non-blocking I/O

### Security and Performance
- Use Quarkus Security for authentication and authorization
- Implement MicroProfile Health, Metrics, and OpenTracing
- Use Quarkus OpenAPI extension for API documentation
- Optimize for GraalVM native image creation

## Blockchain and Smart Contract Development

### Solidity Best Practices
- Use explicit function visibility modifiers and natspec comments
- Utilize function modifiers for common checks
- Follow Checks-Effects-Interactions pattern to prevent reentrancy
- Use OpenZeppelin's libraries for security and standard implementations
- Implement proper access control using OpenZeppelin's AccessControl
- Use custom errors instead of revert strings for gas efficiency

### Testing and Security
- Use static analysis tools like Slither and Mythril
- Implement comprehensive testing with property-based testing
- Conduct regular security audits and bug bounties
- Use circuit breakers (pause functionality) when appropriate

## Content Management Systems

### WordPress and WooCommerce
- Follow WordPress and WooCommerce coding standards
- Use WordPress hooks (actions and filters) for extending functionality
- Implement proper theme functions using functions.php
- Use WordPress's built-in user roles and capabilities system
- Leverage action and filter hooks provided by WooCommerce
- Use WooCommerce's Settings API for plugin configuration pages

### Payload CMS Development
- Structure collections with clear relationships and field validation
- Implement proper access control with field-level permissions
- Create reusable field groups and blocks for content modeling
- Follow the Payload hooks pattern for extending functionality
- Use migrations for database schema changes
- Organize collections by domain or feature

### Sanity CMS Guidelines
- Include appropriate icons using lucide-react or Sanity icons
- Always use named exports with TypeScript definitions
- Use `defineField` on every field and `defineType` throughout
- Structure files with proper folder organization and index files
- Prefer Sanity indexes over filters in GROQ queries

## Enterprise Application Development

### Odoo Development
- Define models using Odoo's ORM by inheriting from models.Model
- Use API decorators such as @api.model, @api.depends, and @api.onchange
- Create and customize UI views using XML for forms, trees, kanban views
- Implement web controllers using the @http.route decorator
- Use Odoo's built-in exceptions for error communication
- Optimize ORM queries using domain filters and computed fields

### Business Application Patterns
- Leverage automated actions and scheduled actions for background processing
- Extend existing functionalities using inheritance mechanisms
- Implement proper access control lists (ACLs) and record rules
- Use internationalization by marking translatable strings with _()

## Specialized Programming Languages

### Lua Programming
- Use local variables whenever possible for better performance
- Utilize Lua's table features effectively for data structures
- Implement proper error handling using pcall/xpcall
- Use metatables and metamethods appropriately
- Follow snake_case for variables and functions, PascalCase for classes/modules

### Elixir and Phoenix
- Follow Phoenix conventions and best practices
- Use functional programming patterns and leverage immutability
- Use Elixir's pattern matching and guards effectively
- Implement proper error logging and user-friendly messages
- Use Ecto changesets for data validation
- Use Phoenix LiveView for dynamic, real-time interactions

### AutoHotkey v2
- Always look for API approach over imitating human actions
- Use camel case for variables, functions and classes (5-25 characters)
- Do NOT use external libraries or dependencies
- Function and class definitions should be at end of script
- Use One True Brace formatting for Functions, Classes, loops, and If statements

## Advanced Package Management

### Python UV Package Manager
- Use `uv` exclusively for Python dependency management
- Never use `pip`, `pip-tools`, or `poetry` directly
- Always use `uv add <package>` to add dependencies
- Use `uv remove <package>` to remove dependencies
- Use `uv sync` to reinstall all dependencies from lock file
- Use `uv run script.py` to run scripts with proper dependencies

## Security and Cybersecurity Tools

### Python Cybersecurity Development
- Use functional, declarative programming; avoid classes where possible
- Organize into modules: scanners/, enumerators/, attackers/, reporting/, utils/
- Sanitize all external inputs; never invoke shell commands with unsanitized strings
- Use secure defaults (TLSv1.2+, strong cipher suites)
- Implement rate-limiting and back-off for network scans
- Use structured logging (JSON) for easy ingestion by SIEMs

### Security Best Practices
- Ensure secrets are loaded from secure stores or environment variables
- Provide both CLI and RESTful API interfaces using RORO pattern
- Utilize asyncio and connection pooling for high-throughput scanning
- Cache DNS lookups and vulnerability database queries when appropriate

## Embedded Systems Development

### Arduino/ESP32/ESP8266
- Use PlatformIO framework with best practices
- Analyze possible approaches before implementation (2-3 options with pros/cons)
- Check Alex Gyver's libraries (https://github.com/gyverlibs) for suitable solutions
- Structure projects according to PlatformIO rules
- Generate platformio.ini with required dependencies
- Follow ISO C++ standards and guidelines

## Technical Writing and Documentation

### Content Creation Guidelines
- Start with technical content immediately; avoid broad introductions
- Use direct, matter-of-fact tone; write as explaining to peer developer
- Focus on 'how' and 'why' of implementations
- Provide substantial, real-world code examples
- Create intentional, meaningful subtitles that add value
- Structure tutorials to build complete implementation

## Model Evaluation and Critique

### Response Quality Assessment
- Evaluate accuracy: Does response correctly address question/task?
- Assess completeness: Does it cover all aspects?
- Check clarity: Is response easy to understand?
- Verify conciseness: Appropriately detailed without unnecessary information?
- Confirm relevance: Stays on topic, avoids tangential information?
- Provide score from 0-10 on quality
- Indicate whether response fully solved question/task

## Universal Development Principles

### Code Quality Standards
- Write clean, efficient, well-documented code
- Follow language-specific best practices
- Create modular, reusable code for flexibility and scalability
- Ensure comprehensive testing strategies
- Prioritize security best practices throughout development
- Optimize performance while maintaining readability
- Implement robust error handling and logging
- Support CI/CD practices
- Design for scalability and future growth

### Cross-Platform Considerations
- Follow API design best practices when applicable
- Maintain consistent coding standards across projects
- Implement proper version control and change management
- Use appropriate architectural patterns for each domain
- Consider performance implications of implementation choices
- Ensure proper documentation and code maintainability