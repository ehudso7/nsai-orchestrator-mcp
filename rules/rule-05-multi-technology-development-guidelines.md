# Rule #5: Multi-Technology Development Guidelines

## Web Scraping and Data Extraction

### Key Principles
- Write concise, technical responses with accurate Python examples
- Prioritize readability, efficiency, and maintainability in scraping workflows
- Use modular and reusable functions to handle common scraping tasks
- Handle dynamic and complex websites using appropriate tools (e.g., Selenium, agentQL)
- Follow PEP 8 style guidelines for Python code

### General Web Scraping
- Use requests for simple HTTP GET/POST requests to static websites
- Parse HTML content with BeautifulSoup for efficient data extraction
- Handle JavaScript-heavy websites with selenium or headless browsers
- Respect website terms of service and use proper request headers (e.g., User-Agent)
- Implement rate limiting and random delays to avoid triggering anti-bot measures

### Text Data Gathering
- Use jina or firecrawl for efficient, large-scale text data extraction
  - Jina: Best for structured and semi-structured data, utilizing AI-driven pipelines
  - Firecrawl: Preferred for crawling deep web content or when data depth is critical
- Use jina when text data requires AI-driven structuring or categorization
- Apply firecrawl for tasks that demand precise and hierarchical exploration

### Handling Complex Processes
- Use agentQL for known, complex processes (e.g., logging in, form submissions)
  - Define clear workflows for steps, ensuring error handling and retries
  - Automate CAPTCHA solving using third-party services when applicable
- Leverage multion for unknown or exploratory tasks
  - Examples: Finding the cheapest plane ticket, purchasing newly announced concert tickets
  - Design adaptable, context-aware workflows for unpredictable scenarios

### Data Validation and Storage
- Validate scraped data formats and types before processing
- Handle missing data by flagging or imputing as required
- Store extracted data in appropriate formats (e.g., CSV, JSON, or databases such as SQLite)
- For large-scale scraping, use batch processing and cloud storage solutions

## Kotlin Android Development

### Basic Principles
- Use English for all code and documentation
- Always declare the type of each variable and function (parameters and return value)
- Avoid using any
- Create necessary types
- Don't leave blank lines within a function

### Nomenclature
- Use PascalCase for classes
- Use camelCase for variables, functions, and methods
- Use underscores_case for file and directory names
- Use UPPERCASE for environment variables
- Avoid magic numbers and define constants
- Start each function with a verb
- Use verbs for boolean variables (isLoading, hasError, canDelete, etc.)
- Use complete words instead of abbreviations and correct spelling

### Functions
- Write short functions with a single purpose. Less than 20 instructions
- Name functions with a verb and something else
- If it returns a boolean, use isX or hasX, canX, etc.
- If it doesn't return anything, use executeX or saveX, etc.
- Avoid nesting blocks by early checks and returns, extraction to utility functions
- Use higher-order functions (map, filter, reduce, etc.) to avoid function nesting
- Use arrow functions for simple functions (less than 3 instructions)
- Use named functions for non-simple functions
- Use default parameter values instead of checking for null or undefined
- Reduce function parameters using RO-RO (use an object to pass multiple parameters)

### Android Specific Principles
- Use clean architecture
- Use repository pattern for data persistence
- Use MVI pattern to manage state and events in viewmodels
- Use Auth Activity to manage authentication flow
- Use Navigation Component to manage navigation between activities/fragments
- Use MainActivity to manage the main navigation
- Use ViewBinding to manage views
- Use Flow/LiveData to manage UI state
- Use xml and fragments instead of jetpack compose
- Use Material 3 for the UI
- Use ConstraintLayout for layouts

## TypeScript and Pixi.js Game Development

### Key Principles
- Write concise, technically accurate TypeScript code with a focus on performance
- Use functional and declarative programming patterns; avoid classes unless necessary
- Prioritize code optimization and efficient resource management for smooth gameplay
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasRendered)
- Structure files logically: game components, scenes, utilities, assets management, and types

### Project Structure and Organization
- Organize code by feature directories (e.g., 'scenes/', 'entities/', 'systems/', 'assets/')
- Use environment variables for different stages (development, staging, production)
- Create build scripts for bundling and deployment
- Implement CI/CD pipeline for automated testing and deployment
- Set up staging and canary environments for testing game builds

### Naming Conventions
- camelCase: functions, variables (e.g., 'createSprite', 'playerHealth')
- kebab-case: file names (e.g., 'game-scene.ts', 'player-component.ts')
- PascalCase: classes and Pixi.js objects (e.g., 'PlayerSprite', 'GameScene')
- Booleans: use prefixes like 'should', 'has', 'is' (e.g., 'shouldRespawn', 'isGameOver')
- UPPERCASE: constants and global variables (e.g., 'MAX_PLAYERS', 'GRAVITY')

### Pixi.js Specific Optimizations
- Use sprite batching and container nesting wisely to reduce draw calls
- Implement texture atlases to optimize rendering and reduce texture swaps
- Utilize Pixi.js's built-in caching mechanisms for complex graphics
- Properly manage the Pixi.js scene graph, removing unused objects and using object pooling
- Use Pixi.js's built-in interaction manager for efficient event handling
- Leverage Pixi.js filters effectively, being mindful of their performance impact
- Use ParticleContainer for large numbers of similar sprites
- Implement culling for off-screen objects to reduce rendering load

## Blockchain Development

### Solana Program Development
- Write Rust code with a focus on safety and performance
- Use Anchor to streamline Solana program development
- Structure smart contract code to be modular and reusable
- Ensure that all accounts, instructions, and data structures are well-defined and documented
- Implement strict access controls and validate all inputs
- Use Solana's native security features for transaction verification
- Optimize smart contracts for low transaction costs and high execution speed

### CosmWasm Smart Contract Development
- Write Rust code adhering to low-level systems programming principles
- Structure smart contract code with clear separation of concerns
- The interface of each smart contract is placed in contract/mod.rs
- Implementation functions are placed in contract/init.rs, contract/exec.rs, contract/query.rs
- Definitions of msg are placed in msg directory
- Define a separate error type and save it in a separate file
- Ensure all data structures are well-defined and documented

### Solidity and Smart Contract Security
- Use explicit function visibility modifiers and appropriate natspec comments
- Utilize function modifiers for common checks, enhancing readability
- Follow consistent naming: CamelCase for contracts, PascalCase for interfaces (prefixed with "I")
- Implement the Interface Segregation Principle for flexible and maintainable contracts
- Follow the Checks-Effects-Interactions pattern to prevent reentrancy
- Use static analysis tools like Slither and Mythril in the development workflow
- Use OpenZeppelin's AccessControl for fine-grained permissions
- Implement circuit breakers (pause functionality) using OpenZeppelin's Pausable

## Web Development Frameworks

### Astro Framework
- Write concise, technical responses with accurate Astro examples
- Leverage Astro's partial hydration and multi-framework support effectively
- Prioritize static generation and minimal JavaScript for optimal performance
- Use descriptive variable names and follow Astro's naming conventions
- Organize files using Astro's file-based routing system

### Elixir and Phoenix
- Write concise, idiomatic Elixir code with accurate examples
- Follow Phoenix conventions and best practices
- Use functional programming patterns and leverage immutability
- Prefer higher-order functions and recursion over imperative loops
- Use descriptive variable and function names
- Use Elixir's pattern matching and guards effectively
- Leverage Phoenix's built-in functions and macros
- Use Ecto effectively for database operations

### WordPress and WooCommerce
- Write concise, technical code with accurate PHP examples
- Follow WordPress and WooCommerce coding standards and best practices
- Use object-oriented programming when appropriate, focusing on modularity
- Prefer iteration and modularization over duplication
- Use descriptive function, variable, and file names
- Favor hooks (actions and filters) for extending functionality
- Use WordPress hooks instead of modifying core files
- Implement proper theme functions using functions.php
- Use WordPress's built-in user roles and capabilities system

## Infrastructure and DevOps

### Terraform and Infrastructure as Code
- Write concise, well-structured Terraform code with accurate examples
- Organize infrastructure resources into reusable modules
- Use versioned modules and provider version locks to ensure consistent deployments
- Avoid hardcoded values; always use variables for flexibility
- Structure files into logical sections: main configuration, variables, outputs, and modules
- Use remote backends (e.g., S3, Azure Blob, GCS) for state management
- Enable state locking and use encryption for security

### DevOps and Azure Cloud Services
- Use English for all code, documentation, and comments
- Prioritize modular, reusable, and scalable code
- Follow naming conventions: camelCase for variables, PascalCase for classes, snake_case for files
- Avoid hard-coded values; use environment variables or configuration files
- Apply Infrastructure-as-Code (IaC) principles where possible
- Use descriptive names for scripts and variables
- Write modular scripts with functions to enhance readability and reuse
- Follow idempotent design principles for all playbooks

## Mobile Development

### Ionic and Cordova
- Organize by feature directories (e.g., 'services/', 'components/', 'pipes/')
- Use environment variables for different stages (development, staging, production)
- Use descriptive names for variables and functions
- Keep classes small and focused
- Avoid global state when possible
- Manage routing through a dedicated module
- Use the latest ES6+ features and best practices for TypeScript and Angular
- Centralize API calls and error handling through services

### Swift 6 and Xcode 16
- Utilize the latest versions of SwiftUI and Swift
- Be familiar with the newest features and best practices
- Provide careful and accurate answers that are well-founded
- Use the Chain-of-Thought (CoT) method in reasoning and answers
- Strictly adhere to requirements and meticulously complete tasks
- Begin by outlining proposed approach with detailed steps or pseudocode
- Emphasize code readability over performance optimization

## Advanced Programming Languages

### Lua Programming
- Write clear, concise Lua code that follows idiomatic patterns
- Leverage Lua's dynamic typing while maintaining code clarity
- Use proper error handling and coroutines effectively
- Follow consistent naming conventions and code organization
- Optimize for performance while maintaining readability
- Use local variables whenever possible for better performance
- Utilize Lua's table features effectively for data structures
- Implement proper error handling using pcall/xpcall
- Use metatables and metamethods appropriately

### JAX and Machine Learning
- Write concise, technical Python code with accurate examples
- Prioritize clarity, efficiency, and best practices in deep learning workflows
- Use object-oriented programming for model architectures
- Use functional programming for data processing pipelines
- Implement proper GPU utilization and mixed precision training
- Use descriptive variable names that reflect the components they represent
- Follow PEP 8 style guidelines for Python code

### Java and Quarkus Framework
- Write clean, efficient, and well-documented Java code using Quarkus best practices
- Follow Jakarta EE and MicroProfile conventions
- Use descriptive method and variable names following camelCase convention
- Structure application with consistent organization
- Leverage Quarkus Dev Mode for faster development cycles
- Use Quarkus annotations effectively
- Implement build-time optimizations using Quarkus extensions

## Testing and Quality Assurance

### General Testing Principles
- Follow the Arrange-Act-Assert convention for tests
- Name test variables clearly
- Write unit tests for each public function
- Use test doubles to simulate dependencies
- Write acceptance tests for each module
- Follow the Given-When-Then convention
- Implement comprehensive testing strategies
- Use property-based testing to uncover edge cases

### Model Evaluation and Critique
- Evaluate accuracy: Does response correctly address question/task?
- Assess completeness: Does it cover all aspects?
- Check clarity: Is response easy to understand?
- Verify conciseness: Appropriately detailed without unnecessary information?
- Confirm relevance: Stays on topic, avoids tangential information?
- Provide score from 0-10 on quality
- Indicate whether response fully solved question/task

## AI and Machine Learning Guidelines

### AI Trajectory Analysis
- Evaluate the correctness of the given question and trajectory
- Provide detailed reasoning and analysis
- Focus on the latest thought, action, and observation
- Consider incomplete trajectories correct if thoughts and actions are valid
- Do not generate additional thoughts or actions
- Conclude analysis with correctness score from 1 to 10

### E-commerce Navigation
- Analyze the user's request for product specifications, preferences, and constraints
- Break down the request into searchable terms and decision criteria
- Use the search function with relevant keywords from the user's request
- Compare products against the user's criteria
- Use the "think" action to reason about which products best match the criteria
- Make decisions based on the best match to user criteria

## Technical Writing and Documentation

### Content Creation Guidelines
- Start with technical content immediately; avoid broad introductions
- Use direct, matter-of-fact tone; write as explaining to peer developer
- Focus on 'how' and 'why' of implementations
- Provide substantial, real-world code examples
- Create intentional, meaningful subtitles that add value
- Structure tutorials to build complete implementation

### Documentation Standards
- Document complex logic and non-obvious code decisions
- Follow official documentation for best practices
- Include docstrings for functions and modules
- Comment on complex or non-obvious code sections
- Maintain API documentation
- Include usage examples for public interfaces

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

### Security Best Practices
- Implement proper authentication and authorization
- Use HTTPS and TLS for secure communication
- Implement input validation and sanitization
- Use proper secrets management
- Implement security scanning and vulnerability assessment
- Follow security guidelines and best practices

### Performance Optimization
- Use proper caching strategies
- Implement database query optimization
- Use CDNs for static content delivery
- Implement proper monitoring and profiling
- Use async programming for I/O-bound operations
- Implement proper resource management

Refer to official documentation for each technology and stay updated with latest best practices and features.