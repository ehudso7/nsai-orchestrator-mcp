# Rule #9: Additional Development Guidelines

## Python and Backend Development

### FastAPI and Web Development
- Write concise, technical responses with accurate Python examples
- Use functional, declarative programming; avoid classes where possible
- Use type hints for all function signatures; prefer Pydantic models for input validation
- Use async def for asynchronous operations and def for pure functions
- Handle errors at the beginning of functions with early returns
- Use HTTPException for expected errors and proper error handling
- Optimize for performance using async functions for I/O-bound tasks

### Python Package Management with `uv`
- Use `uv` exclusively for Python dependency management
- Always use these commands:
  - `uv add <package>` - Add or upgrade dependencies
  - `uv remove <package>` - Remove dependencies  
  - `uv sync` - Reinstall all dependencies from lock file
  - `uv run script.py` - Run script with proper dependencies

### Django Development
- Use Django's built-in features and tools wherever possible
- Leverage Django's ORM for database interactions
- Use class-based views (CBVs) for complex views; function-based views (FBVs) for simpler logic
- Follow the MVT (Model-View-Template) pattern strictly
- Use Django's validation framework and security best practices

## Specialized Development Areas

### Cybersecurity Tool Development
- Use functional, declarative programming for security tools
- Organize file structure into modules: `scanners/`, `enumerators/`, `attackers/`, `reporting/`, `utils/`
- Sanitize all external inputs; never invoke shell commands with unsanitized strings
- Use secure defaults (TLSv1.2+, strong cipher suites)
- Implement rate-limiting and back-off for network scans
- Use structured logging (JSON) for easy ingestion by SIEMs

### Arduino/ESP32/ESP8266 Development
- Use PlatformIO framework with best practices
- Analyze possible approaches before implementation
- Check Alex Gyver's libraries (https://github.com/gyverlibs) for suitable solutions
- Structure projects according to PlatformIO rules
- Generate platformio.ini with required dependencies
- Follow ISO C++ standards and guidelines
- Check code for errors after writing or correcting

### AutoHotkey v2 Development
- Always look for API approach over imitating human actions
- Use camel case for variables, functions and classes (5-25 characters)
- Do NOT use external libraries or dependencies
- Function and class definitions at end of script
- Use One True Brace formatting
- Add standard headers and hotkeys to each script

### Drupal 10 Module Development
- Follow SOLID principles and modern PHP features (PHP 8.1+)
- Use strict typing: `declare(strict_types=1);`
- Use Drupal's database API instead of raw SQL
- Implement Repository pattern for data access logic
- Use Drupal's service container for dependency injection
- Leverage Drupal's caching API for performance
- Follow Drupal coding standards and best practices

## Data Science and Analysis

### Jupyter Notebook Development
- Structure notebooks with clear sections using markdown cells
- Use meaningful cell execution order for reproducibility
- Keep code cells focused and modular
- Implement data quality checks at beginning of analysis
- Use vectorized operations in pandas and numpy
- Create reusable plotting functions for consistent visualizations

### Machine Learning and AI
- Use PyTorch as primary framework for deep learning
- Implement custom nn.Module classes for model architectures
- Use Transformers library for pre-trained models
- Use Diffusers library for diffusion models
- Create modular code structures with separate files for models, data loading, training
- Implement proper experiment tracking and model checkpointing

## Game Development

### Pixi.js and Web Games
- Write performance-focused TypeScript code
- Use functional programming patterns; avoid classes unless necessary
- Organize by feature directories: 'scenes/', 'entities/', 'systems/', 'assets/'
- Use Pixi.js best practices for rendering and object pooling
- Implement texture atlases and sprite batching
- Optimize for both web and mobile performance

## Content Management

### Sanity CMS Development
- Include appropriate icons using lucide-react or Sanity icons
- Always use named exports with TypeScript definitions
- Use `defineField` on every field and `defineType` throughout
- Structure files with proper folder organization and index files
- Generate types after schema changes
- Prefer Sanity indexes over filters in GROQ queries

## Testing and Quality Assurance

### Playwright End-to-End Testing
- Use descriptive test names that clearly describe expected behavior
- Use Playwright fixtures for test isolation and consistency
- Avoid `page.locator`; use recommended built-in locators
- Use `page.getByTestId` when `data-testid` is defined
- Prefer web-first assertions (`toBeVisible`, `toHaveText`)
- Avoid hardcoded timeouts; use `page.waitFor` with conditions

## Key Universal Principles

1. **Security First**: Always implement proper authentication, input validation, and secure practices
2. **Performance Optimization**: Optimize for both development and runtime performance
3. **Type Safety**: Use strong typing throughout codebases
4. **Error Handling**: Implement comprehensive error handling and user-friendly messages
5. **Testing**: Write unit, integration, and end-to-end tests
6. **Documentation**: Document all public APIs and complex logic
7. **Accessibility**: Ensure applications are accessible to all users
8. **Monitoring**: Implement proper logging, monitoring, and analytics

Follow official documentation for each technology and stay updated with latest best practices.