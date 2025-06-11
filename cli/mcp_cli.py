#!/usr/bin/env python3
"""
NSAI Orchestrator MCP Command Line Interface

Production-grade CLI for managing and interacting with the MCP system.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import argparse
import subprocess
import os
import requests
from datetime import datetime

import structlog

# Configure logging for CLI
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer(colors=True)
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class MCPCLIClient:
    """CLI client for MCP Orchestrator."""
    
    def __init__(self, base_url: str = "http://localhost:4141", api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"text": response.text}
                
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to MCP server at {self.base_url}")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Request failed: {e}")
            sys.exit(1)
    
    def status(self) -> Dict[str, Any]:
        """Get server status."""
        return self._request("GET", "/")
    
    def health(self) -> Dict[str, Any]:
        """Get server health."""
        return self._request("GET", "/health")
    
    def execute_task(self, agent: str, method: str = "execute", **params) -> Dict[str, Any]:
        """Execute task with agent."""
        payload = {
            "method": method,
            "params": {
                "agent": agent,
                **params
            }
        }
        return self._request("POST", "/mcp", json=payload)
    
    def get_memory_graph(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get memory graph."""
        params = filters or {}
        return self._request("GET", "/memory/graph", params=params)
    
    def query_memory(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Query memory system."""
        return self._request("POST", "/memory/query", json=query)


class MCPCLICommands:
    """CLI command implementations."""
    
    def __init__(self, client: MCPCLIClient):
        self.client = client
    
    def status(self, args):
        """Show server status."""
        logger.info("Checking MCP server status...")
        
        try:
            status = self.client.status()
            health = self.client.health()
            
            print("\n🤖 NSAI Orchestrator MCP Status")
            print("=" * 40)
            print(f"Service: {status.get('service', 'Unknown')}")
            print(f"Version: {status.get('version', 'Unknown')}")
            print(f"Status: {status.get('status', 'Unknown')}")
            print(f"Environment: {status.get('environment', 'Unknown')}")
            
            if health.get('system'):
                system = health['system']
                print(f"\n📊 System Metrics:")
                print(f"  CPU Usage: {system.get('cpu_percent', 0):.1f}%")
                print(f"  Memory Usage: {system.get('memory_percent', 0):.1f}%")
                print(f"  Disk Usage: {system.get('disk_percent', 0):.1f}%")
            
            uptime = health.get('uptime_seconds', 0)
            if uptime:
                hours = uptime // 3600
                minutes = (uptime % 3600) // 60
                print(f"  Uptime: {int(hours)}h {int(minutes)}m")
            
            # Health status
            health_status = health.get('status', 'unknown')
            status_emoji = "🟢" if health_status == "healthy" else "🟡" if health_status == "warning" else "🔴"
            print(f"\n{status_emoji} Health: {health_status}")
            
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            sys.exit(1)
    
    def execute(self, args):
        """Execute a task."""
        logger.info(f"Executing task with {args.agent} agent...")
        
        # Prepare parameters
        params = {"task": args.task}
        
        if args.data:
            try:
                params.update(json.loads(args.data))
            except json.JSONDecodeError:
                logger.error("Invalid JSON data provided")
                sys.exit(1)
        
        try:
            start_time = time.time()
            result = self.client.execute_task(args.agent, args.method, **params)
            duration = time.time() - start_time
            
            print(f"\n🚀 Task Execution Result")
            print("=" * 40)
            print(f"Agent: {args.agent}")
            print(f"Method: {args.method}")
            print(f"Duration: {duration:.2f}s")
            print(f"Success: {'✅' if result.get('success') else '❌'}")
            
            if result.get('success'):
                if 'result' in result:
                    print(f"\n📋 Result:")
                    print(json.dumps(result['result'], indent=2))
                if 'task_id' in result:
                    print(f"\n🆔 Task ID: {result['task_id']}")
            else:
                print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            sys.exit(1)
    
    def memory(self, args):
        """Memory operations."""
        if args.memory_action == "graph":
            self._memory_graph(args)
        elif args.memory_action == "search":
            self._memory_search(args)
        elif args.memory_action == "query":
            self._memory_query(args)
    
    def _memory_graph(self, args):
        """Get memory graph."""
        logger.info("Retrieving memory graph...")
        
        try:
            filters = {}
            if args.session_id:
                filters['session_id'] = args.session_id
            
            result = self.client.get_memory_graph(filters)
            
            if result.get('success'):
                graph_data = result.get('data', {})
                nodes = graph_data.get('nodes', [])
                edges = graph_data.get('edges', [])
                
                print(f"\n🧠 Memory Graph")
                print("=" * 40)
                print(f"Nodes: {len(nodes)}")
                print(f"Edges: {len(edges)}")
                
                if args.details and nodes:
                    print(f"\n📋 Recent Nodes:")
                    for node in nodes[:5]:  # Show first 5 nodes
                        print(f"  • {node.get('id', 'unknown')} ({node.get('label', 'unknown')})")
                        if len(node.get('content', '')) > 100:
                            print(f"    Content: {node['content'][:100]}...")
                        else:
                            print(f"    Content: {node.get('content', '')}")
                
                if args.export:
                    with open(args.export, 'w') as f:
                        json.dump(graph_data, f, indent=2)
                    print(f"\n💾 Graph exported to {args.export}")
            else:
                logger.error(f"Failed to get memory graph: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Memory graph retrieval failed: {e}")
            sys.exit(1)
    
    def _memory_search(self, args):
        """Search memory."""
        logger.info(f"Searching memory for: {args.query}")
        
        try:
            query_data = {
                "query_type": "search",
                "filters": {
                    "content_contains": args.query
                },
                "limit": args.limit or 10
            }
            
            if args.session_id:
                query_data["filters"]["session_id"] = args.session_id
            
            result = self.client.query_memory(query_data)
            
            if result.get('success'):
                nodes = result.get('result', {}).get('nodes', [])
                
                print(f"\n🔍 Memory Search Results")
                print("=" * 40)
                print(f"Query: {args.query}")
                print(f"Found: {len(nodes)} nodes")
                
                for i, node in enumerate(nodes, 1):
                    print(f"\n{i}. {node.get('id', 'unknown')} ({node.get('label', 'unknown')})")
                    content = node.get('content', '')
                    if len(content) > 200:
                        print(f"   {content[:200]}...")
                    else:
                        print(f"   {content}")
                    
                    if node.get('tags'):
                        print(f"   Tags: {', '.join(node['tags'])}")
            else:
                logger.error(f"Memory search failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            sys.exit(1)
    
    def _memory_query(self, args):
        """Execute memory query."""
        if not args.query_file:
            logger.error("Query file required for memory query")
            sys.exit(1)
        
        try:
            with open(args.query_file, 'r') as f:
                query_data = json.load(f)
            
            result = self.client.query_memory(query_data)
            
            print(f"\n🔍 Memory Query Result")
            print("=" * 40)
            print(json.dumps(result, indent=2))
            
        except FileNotFoundError:
            logger.error(f"Query file not found: {args.query_file}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in query file")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Memory query failed: {e}")
            sys.exit(1)
    
    def init(self, args):
        """Initialize MCP project."""
        project_dir = Path(args.directory)
        
        if project_dir.exists() and any(project_dir.iterdir()):
            if not args.force:
                logger.error(f"Directory {project_dir} is not empty. Use --force to override.")
                sys.exit(1)
        
        logger.info(f"Initializing MCP project in {project_dir}")
        
        # Create directory structure
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic files
        files_to_create = {
            ".env.example": self._get_env_template(),
            "docker-compose.yml": self._get_docker_compose_template(),
            "README.md": self._get_readme_template(),
            "config.py": "# Configuration will be generated here",
            ".gitignore": self._get_gitignore_template(),
        }
        
        for filename, content in files_to_create.items():
            file_path = project_dir / filename
            if not file_path.exists() or args.force:
                file_path.write_text(content)
                logger.info(f"Created {filename}")
        
        # Create plugins directory
        plugins_dir = project_dir / "plugins"
        plugins_dir.mkdir(exist_ok=True)
        (plugins_dir / "README.md").write_text("# Custom Agent Plugins\n\nPlace your custom agent plugins here.")
        
        print(f"\n✅ MCP project initialized in {project_dir}")
        print(f"\nNext steps:")
        print(f"1. Copy .env.example to .env and configure your settings")
        print(f"2. Run: docker-compose up -d")
        print(f"3. Visit http://localhost:4141 to access the API")
        print(f"4. Visit http://localhost:3000 to access the frontend")
    
    def _get_env_template(self) -> str:
        """Get .env template."""
        return """# NSAI Orchestrator MCP Configuration

# Application
APP_NAME="NSAI Orchestrator MCP"
ENVIRONMENT="development"
DEBUG="true"

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY="your-super-secret-key-change-this"
JWT_SECRET="your-jwt-secret-change-this"

# API Keys (REQUIRED)
ANTHROPIC_API_KEY="your-anthropic-api-key"
OPENAI_API_KEY="your-openai-api-key"

# Database
REDIS_HOST="redis"
NEO4J_URI="bolt://neo4j:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="password"

# Ports
PORT="4141"
FRONTEND_PORT="3000"
"""
    
    def _get_docker_compose_template(self) -> str:
        """Get docker-compose template."""
        return """version: '3.8'

services:
  backend:
    image: ghcr.io/nsai-team/orchestrator-mcp:latest
    ports:
      - "${PORT:-4141}:4141"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - NEO4J_URI=bolt://neo4j:7687
      - REDIS_HOST=redis
    depends_on:
      - redis
      - neo4j
    restart: unless-stopped

  frontend:
    image: ghcr.io/nsai-team/orchestrator-mcp-frontend:latest
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:${PORT:-4141}
    depends_on:
      - backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  neo4j:
    image: neo4j:5
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD:-password}
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
    restart: unless-stopped

volumes:
  redis_data:
  neo4j_data:
"""
    
    def _get_readme_template(self) -> str:
        """Get README template."""
        return """# NSAI Orchestrator MCP

Production-grade multi-agent orchestration platform.

## Quick Start

1. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. Start services:
   ```bash
   docker-compose up -d
   ```

3. Access the application:
   - API: http://localhost:4141
   - Frontend: http://localhost:3000
   - Neo4j Browser: http://localhost:7474

## CLI Usage

```bash
# Check status
mcp-cli status

# Execute task
mcp-cli execute claude "Analyze this data"

# View memory graph
mcp-cli memory graph --details
```

## Documentation

For full documentation, visit: https://nsai-team.github.io/orchestrator-mcp
"""
    
    def _get_gitignore_template(self) -> str:
        """Get .gitignore template."""
        return """.env
*.log
*.pyc
__pycache__/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
node_modules/
.next/
dist/
build/
*.egg-info/
.DS_Store
"""


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="NSAI Orchestrator MCP CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcp-cli status
  mcp-cli execute claude "Analyze system performance"
  mcp-cli execute codex "Generate API client code"
  mcp-cli memory graph --export graph.json
  mcp-cli memory search "error handling"
  mcp-cli init my-mcp-project
        """
    )
    
    parser.add_argument(
        "--api-url",
        default=os.getenv("MCP_API_URL", "http://localhost:4141"),
        help="MCP API base URL"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("MCP_API_KEY"),
        help="API key for authentication"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show server status")
    
    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute a task")
    execute_parser.add_argument("agent", help="Agent to use (claude, codex, orchestrator, memory)")
    execute_parser.add_argument("task", help="Task description")
    execute_parser.add_argument("--method", default="execute", help="Method to call")
    execute_parser.add_argument("--data", help="Additional data as JSON")
    
    # Memory command
    memory_parser = subparsers.add_parser("memory", help="Memory operations")
    memory_subparsers = memory_parser.add_subparsers(dest="memory_action", help="Memory actions")
    
    # Memory graph
    graph_parser = memory_subparsers.add_parser("graph", help="Get memory graph")
    graph_parser.add_argument("--session-id", help="Filter by session ID")
    graph_parser.add_argument("--details", action="store_true", help="Show detailed information")
    graph_parser.add_argument("--export", help="Export graph to JSON file")
    
    # Memory search
    search_parser = memory_subparsers.add_parser("search", help="Search memory")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--session-id", help="Filter by session ID")
    search_parser.add_argument("--limit", type=int, help="Limit results")
    
    # Memory query
    query_parser = memory_subparsers.add_parser("query", help="Execute memory query")
    query_parser.add_argument("--query-file", required=True, help="JSON file with query")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize MCP project")
    init_parser.add_argument("directory", help="Project directory")
    init_parser.add_argument("--force", action="store_true", help="Force initialization in non-empty directory")
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.verbose:
        # Enable debug logging
        structlog.configure(
            processors=[
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            wrapper_class=structlog.make_filtering_bound_logger(10),  # DEBUG level
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create client
    client = MCPCLIClient(args.api_url, args.api_key)
    commands = MCPCLICommands(client)
    
    # Execute command
    try:
        command_func = getattr(commands, args.command)
        command_func(args)
    except AttributeError:
        logger.error(f"Unknown command: {args.command}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()