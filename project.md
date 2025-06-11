# NSAI Orchestrator MCP

## Project Description
A sophisticated Multi-Component Protocol (MCP) orchestration system that coordinates multiple AI agents for complex task execution, analysis, and memory management.

## Core Components

### AI Agents
- **Claude Analyst** (`agents/claude_analyst.py`) - Advanced analysis and reasoning
- **Codex Runner** (`agents/codex_runner.py`) - Code execution and evaluation
- **Memory Graph** (`agents/memory_graph.py`) - Memory management and graph operations
- **Orchestrator Agent** (`agents/orchestrator_agent.py`) - Task coordination and workflow management

### Memory System
- **Graph Driver** (`memory/graph_driver.py`) - Graph database operations
- **Memory Cache** (`memory/memory_cache.py`) - Caching layer for performance

### Utilities
- **LLM Client** (`utils/llm_client.py`) - Language model interface
- **Task Logger** (`utils/task_logger.py`) - Logging and monitoring
- **I/O Utils** (`utils/io_utils.py`) - Input/output utilities

### Frontend
- **Next.js Application** - Modern React-based user interface
- **TypeScript** - Type-safe frontend development
- **Tailwind CSS** - Utility-first styling

## Technology Stack
- **Backend**: Python 3.x
- **Frontend**: Next.js, React, TypeScript
- **Styling**: Tailwind CSS
- **Containerization**: Docker
- **Protocol**: MCP (Multi-Component Protocol)

## Key Features
- Multi-agent orchestration
- Graph-based memory management
- Real-time task coordination
- Web-based interface
- Docker containerization
- Extensible agent architecture

## Use Cases
- Complex multi-step task automation
- AI-powered analysis workflows
- Memory-persistent agent interactions
- Scalable AI orchestration