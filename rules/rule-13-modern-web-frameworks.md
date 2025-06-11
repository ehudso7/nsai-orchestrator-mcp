# Rule #8: Modern Web Development Frameworks

## React, Next.js, and TypeScript Core Principles

- Write concise, technical TypeScript code with accurate examples
- Use functional and declarative programming patterns; avoid classes
- Prefer iteration and modularization over code duplication
- Use descriptive variable names with auxiliary verbs (e.g., `isLoading`, `hasError`)
- Structure files: exported component, subcomponents, helpers, static content, types

## Code Style and Structure

- Use lowercase with dashes for directories (e.g., `components/auth-wizard`)
- Favor named exports for components
- Use TypeScript for all code; prefer interfaces over types
- Avoid enums; use maps instead
- Use functional components with TypeScript interfaces

## Syntax and Formatting

- Use the "function" keyword for pure functions
- Avoid unnecessary curly braces in conditionals; use concise syntax for simple statements
- Use declarative JSX

## UI and Styling

- Use Shadcn UI, Radix, and Tailwind for components and styling
- Implement responsive design with Tailwind CSS; use a mobile-first approach
- Use Next UI and Tailwind CSS for styling

## Performance Optimization

- Minimize 'use client', 'useEffect', and 'setState'; favor React Server Components (RSC)
- Wrap client components in Suspense with fallback
- Use dynamic loading for non-critical components
- Optimize images: use WebP format, include size data, implement lazy loading

## Next.js Specific Guidelines

### App Router and SSR
- Use Next.js App Router for routing
- Favor server components and Next.js SSR features where possible
- Minimize the usage of client components ('use client') to small, isolated components
- Always add loading and error states to data fetching components

### Error Handling
- Implement error handling and error logging
- Use error boundaries for unexpected errors
- Handle errors and edge cases at the beginning of functions
- Use early returns for error conditions to avoid deeply nested if statements

## State Management

- Use 'nuqs' for URL search parameter state management
- Use Zustand for global state management
- Use TanStack React Query for data fetching, caching, and synchronization
- Minimize the use of `useEffect` and `setState`

## Vue.js and Nuxt 3 Guidelines

### Vue 3 Core Principles
- Prefer Composition API `<script setup>` style
- Use Composables to encapsulate and share reusable client-side logic
- Use Nuxt 3's auto imports for 'ref', 'useState', 'useRouter'

### Nuxt 3 Specific Features
- Use `@nuxtjs/color-mode` with `useColorMode()` for color mode handling
- Use Server API (within the server/api directory) for server-side operations
- Use `useRuntimeConfig` for runtime configuration variables
- For SEO use `useHead` and `useSeoMeta`
- Use `<NuxtImage>` or `<NuxtPicture>` for images and Nuxt Icons module for icons

### Data Fetching in Nuxt 3
1. Use `useFetch` for standard data fetching in components
2. Use `$fetch` for client-side requests within event handlers
3. Use `useAsyncData` for complex data fetching logic
4. Set `server: false` to fetch data only on client side
5. Set `lazy: true` to defer non-critical data fetching

## Flutter Development Guidelines

### Clean Architecture Principles
- Strictly adhere to Clean Architecture layers: Presentation, Domain, and Data
- Follow the dependency rule: dependencies always point inward
- Use Feature-first organization with self-contained modules

### Flutter Specific Patterns
- Use Bloc for complex event-driven logic and Cubit for simpler state management
- Implement properly typed Events and States for each Bloc
- Use Freezed for immutable state and union types
- Use GetIt as a service locator for dependency injection

### Error Handling in Flutter
- Use Either<Failure, Success> from Dartz for functional error handling
- Create custom Failure classes for domain-specific errors
- Left represents failure case, Right represents success case

## Key Conventions Across Frameworks

1. **Performance First**: Optimize Web Vitals (LCP, CLS, FID)
2. **Type Safety**: Use TypeScript throughout; prefer strict typing
3. **Error Handling**: Prioritize error handling and edge cases
4. **Accessibility**: Ensure interfaces are keyboard navigable with proper ARIA labels
5. **Testing**: Implement unit, integration, and end-to-end tests
6. **Security**: Implement proper authentication, input validation, and secure practices

## Mobile Development (React Native/Expo)

- Use Expo's managed workflow for streamlined development
- Use SafeAreaProvider for managing safe areas globally
- Implement proper error boundaries and logging
- Use react-navigation for routing and navigation
- Follow performance optimization with proper memoization

## Modern Tooling and Best Practices

- Use modern build tools (Vite, Next.js, Nuxt)
- Implement proper CI/CD pipelines
- Use environment variables for configuration
- Follow semantic versioning and proper release processes
- Monitor application performance and user experience

Follow official documentation for each framework and stay updated with the latest best practices and features.