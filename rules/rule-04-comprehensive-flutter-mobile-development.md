# Rule #4: Comprehensive Flutter and Mobile Development Guidelines

## Flutter Core Development Principles

### Key Principles
- Write concise, technical Dart code with accurate examples
- Use functional and declarative programming patterns where appropriate
- Prefer composition over inheritance
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError)
- Structure files: exported widget, subwidgets, helpers, static content, types

### Dart/Flutter Best Practices
- Use const constructors for immutable widgets
- Leverage Freezed for immutable state classes and unions
- Use arrow syntax for simple functions and methods
- Prefer expression bodies for one-line getters and setters
- Use trailing commas for better formatting and diffs

## Flutter with Riverpod and Supabase

### Riverpod-Specific Guidelines
- Use @riverpod annotation for generating providers
- Prefer AsyncNotifierProvider and NotifierProvider over StateProvider
- Avoid StateProvider, StateNotifierProvider, and ChangeNotifierProvider
- Use ref.invalidate() for manually triggering provider updates
- Implement proper cancellation of asynchronous operations when widgets are disposed

### Supabase Integration
- Use the Supabase client for database interactions and real-time subscriptions
- Implement Row Level Security (RLS) policies for fine-grained access control
- Use Supabase Auth for user authentication and management
- Leverage Supabase Storage for file uploads and management

### Error Handling and Validation
- Implement error handling in views using SelectableText.rich instead of SnackBars
- Display errors in SelectableText.rich with red color for visibility
- Handle empty states within the displaying screen
- Use AsyncValue for proper error handling and loading states

## Flutter with Bloc and Firebase

### Bloc-Specific Guidelines
- Use Cubit for managing simple state and Bloc for complex event-driven state management
- Extend states with Freezed for immutability
- Use descriptive and meaningful event names for Bloc
- Handle state transitions and side effects in Bloc's mapEventToState
- Prefer context.read() or context.watch() for accessing Cubit/Bloc states in widgets

### Firebase Integration Guidelines
- Use Firebase Authentication for user sign-in, sign-up, and password management
- Integrate Firestore for real-time database interactions with structured and normalized data
- Implement Firebase Storage for file uploads and downloads with proper error handling
- Use Firebase Analytics for tracking user behavior and app performance
- Handle Firebase exceptions with detailed error messages and appropriate logging
- Secure database rules in Firestore and Storage based on user roles and permissions

## Flutter Clean Architecture with flutter_bloc

### Clean Architecture Principles
- Strictly adhere to the Clean Architecture layers: Presentation, Domain, and Data
- Follow the dependency rule: dependencies always point inward
- Domain layer contains entities, repositories (interfaces), and use cases
- Data layer implements repositories and contains data sources and models
- Presentation layer contains UI components, blocs, and view models

### Feature-First Organization
- Organize code by features instead of technical layers
- Each feature is a self-contained module with its own implementation of all layers
- Core or shared functionality goes in a separate 'core' directory
- Features should have minimal dependencies on other features

### Directory Structure
```
lib/
├── core/                          # Shared/common code
│   ├── error/                     # Error handling, failures
│   ├── network/                   # Network utilities, interceptors
│   ├── utils/                     # Utility functions and extensions
│   └── widgets/                   # Reusable widgets
├── features/                      # All app features
│   ├── feature_a/                 # Single feature
│   │   ├── data/                  # Data layer
│   │   │   ├── datasources/       # Remote and local data sources
│   │   │   ├── models/            # DTOs and data models
│   │   │   └── repositories/      # Repository implementations
│   │   ├── domain/                # Domain layer
│   │   │   ├── entities/          # Business objects
│   │   │   ├── repositories/      # Repository interfaces
│   │   │   └── usecases/          # Business logic use cases
│   │   └── presentation/          # Presentation layer
│   │       ├── bloc/              # Bloc/Cubit state management
│   │       ├── pages/             # Screen widgets
│   │       └── widgets/           # Feature-specific widgets
└── main.dart                      # Entry point
```

### Dependency Injection
- Use GetIt as a service locator for dependency injection
- Register dependencies by feature in separate files
- Implement lazy initialization where appropriate
- Use factories for transient objects and singletons for services

### Error Handling with Dartz
- Use Either<Failure, Success> from Dartz for functional error handling
- Create custom Failure classes for domain-specific errors
- Left represents failure case, Right represents success case
- Use flatMap/bind for sequential operations that could fail

## Performance Optimization

### General Performance
- Use const widgets where possible to optimize rebuilds
- Implement list view optimizations (e.g., ListView.builder)
- Use AssetImage for static images and cached_network_image for remote images
- Minimize widget rebuilds with proper state management

### Advanced Performance
- Use computation isolation for expensive operations with compute()
- Implement pagination for large data sets
- Cache network resources appropriately
- Profile and optimize render performance

## UI and Styling Guidelines

### UI Components
- Use Flutter's built-in widgets and create custom widgets
- Implement responsive design using LayoutBuilder or MediaQuery
- Use themes for consistent styling across the app
- Use Theme.of(context).textTheme.titleLarge instead of headline6

### Widget Structure
- Create small, private widget classes instead of methods like Widget _build...
- Implement RefreshIndicator for pull-to-refresh functionality
- In TextFields, set appropriate textCapitalization, keyboardType, and textInputAction
- Always include an errorBuilder when using Image.network

## Model and Database Conventions
- Include createdAt, updatedAt, and isDeleted fields in database tables
- Use @JsonSerializable(fieldRename: FieldRename.snake) for models
- Implement @JsonKey(includeFromJson: true, includeToJson: false) for read-only fields
- Use @JsonValue(int) for enums that go to the database

## Key Conventions
1. Use GoRouter or auto_route for navigation and deep linking
2. Optimize for Flutter performance metrics (first meaningful paint, time to interactive)
3. Prefer stateless widgets:
   - Use ConsumerWidget with Riverpod for state-dependent widgets
   - Use HookConsumerWidget when combining Riverpod and Flutter Hooks
   - Use BlocBuilder for widgets that depend on Cubit/Bloc state
   - Use BlocListener for handling side effects

## Testing Strategy
- Write unit tests for domain logic, repositories, and Blocs
- Implement integration tests for features
- Create widget tests for UI components
- Use mocks for dependencies with mockito or mocktail
- Follow Given-When-Then pattern for test structure

## Code Generation
- Utilize build_runner for generating code from annotations (Freezed, Riverpod, JSON serialization)
- Run 'flutter pub run build_runner build --delete-conflicting-outputs' after modifying annotated classes

## Cross-Platform Development Extensions

### SwiftUI Guidelines (iOS Native)
- Use latest version of SwiftUI and Swift with latest features and best practices
- Follow step-by-step planning in pseudocode before implementation
- Write correct, up-to-date, bug-free, fully functional and working code
- Focus on readability over performance
- Leave no todos, placeholders or missing pieces

### Chrome Extension Development
- Write clear, modular TypeScript code with proper type definitions
- Follow functional programming patterns; avoid classes
- Strictly follow Manifest V3 specifications
- Divide responsibilities between background, content scripts and popup
- Use chrome.* APIs correctly (storage, tabs, runtime, etc.)

### Game Development with Unity/C#
- Use MonoBehaviour for script components attached to GameObjects
- Leverage Unity's physics engine and collision detection system
- Use Unity's Input System for handling player input across multiple platforms
- Follow the Component pattern strictly for clear separation of concerns
- Use Coroutines for time-based operations and asynchronous tasks

### Web Game Development with Pixi.js/TypeScript
- Write performance-focused TypeScript code
- Use functional programming patterns; avoid classes unless necessary
- Organize by feature directories: 'scenes/', 'entities/', 'systems/', 'assets/'
- Use Pixi.js best practices for rendering and object pooling
- Implement texture atlases and sprite batching

## Advanced Development Patterns

### State Management Patterns
- Use classes for complex state management (state machines)
- Implement proper experiment tracking and model checkpointing
- Use reactive programming patterns effectively
- Leverage signals system for efficient reactive state management

### Testing and Quality Assurance
- Implement unit tests for utility functions and hooks
- Use integration tests for complex components and pages
- Implement end-to-end tests for critical user flows
- Use comprehensive testing strategies and methodologies

### Security Best Practices
- Implement proper authentication and authorization
- Use HTTPS and TLS for secure communication
- Implement input validation and sanitization
- Use proper secrets management
- Follow security guidelines and best practices

## Universal Development Principles

### Code Quality Standards
- Write clean, efficient, well-documented code
- Follow language-specific best practices
- Create modular, reusable code for flexibility and scalability
- Ensure comprehensive testing strategies
- Prioritize security best practices throughout development

### Documentation and Maintenance
- Document complex logic and non-obvious code decisions
- Follow official documentation for best practices
- Keep documentation up-to-date with setup instructions
- Maintain clear and concise README files

### Performance Considerations
- Use appropriate data structures and algorithms
- Consider time and space complexity
- Optimize resource usage where necessary
- Profile code to identify and optimize bottlenecks

Refer to Flutter, Dart, Riverpod, Bloc, Firebase, and Supabase documentation for detailed implementation guidelines and best practices.