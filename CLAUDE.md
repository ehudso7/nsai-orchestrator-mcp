# Claude Code Configuration

## Project Overview
NSAI Orchestrator MCP - A Multi-Component Protocol (MCP) orchestration system with AI agents for analysis, code execution, and memory management.

## Architecture
- **Backend**: Python-based MCP server with multiple specialized agents
- **Frontend**: Next.js React application
- **Agents**: Claude Analyst, Codex Runner, Memory Graph, Orchestrator Agent
- **Memory**: Graph-based memory system with caching
- **Utils**: LLM client, task logging, I/O utilities

## Key Commands
- `python main.py` - Start the main orchestrator
- `python mcp_server.py` - Start MCP server
- `python test_mcp.py` - Run MCP tests
- `cd frontend && npm run dev` - Start frontend development server
- `cd frontend && npm run build` - Build frontend for production
- `cd frontend && npm run lint` - Lint frontend code

## File Structure
- `/agents/` - AI agent implementations
- `/memory/` - Memory management system
- `/utils/` - Utility functions and helpers
- `/frontend/` - Next.js React frontend
- `/rules/` - Development rules and guidelines for various technologies
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Docker orchestration

## Development Guidelines
- Follow existing code patterns and conventions
- Use type hints in Python code
- Maintain consistent error handling
- Test changes with `test_mcp.py` before committing
- Use the memory graph for persistent state management
- Refer to `/rules/` directory for technology-specific development guidelines
- Follow the comprehensive rules for AI trajectory analysis, web frameworks, and specialized development areas