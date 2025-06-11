"""Enhanced agent management system with plugin support."""

import asyncio
import time
import importlib
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from pathlib import Path

import structlog
from config import get_settings
from core.logging import agent_logger
from schemas import AgentInfo, PluginManifest

logger = structlog.get_logger()
settings = get_settings()


class AgentManager:
    """Enhanced agent management with plugin support."""
    
    def __init__(self, memory_system):
        self.memory_system = memory_system
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.plugins: Dict[str, PluginManifest] = {}
        self.agent_stats: Dict[str, Dict[str, Any]] = {}
        self.plugin_directory = Path("plugins")
    
    async def initialize(self):
        """Initialize agent manager and load agents."""
        try:
            # Load built-in agents
            await self._load_builtin_agents()
            
            # Load plugin agents
            await self._load_plugin_agents()
            
            # Initialize agent statistics
            for agent_name in self.agents.keys():
                self.agent_stats[agent_name] = {
                    "total_tasks": 0,
                    "successful_tasks": 0,
                    "failed_tasks": 0,
                    "total_duration_ms": 0.0,
                    "last_activity": None
                }
            
            logger.info("Agent manager initialized", agent_count=len(self.agents))
            
        except Exception as e:
            logger.error("Failed to initialize agent manager", error=str(e))
            raise
    
    async def cleanup(self):
        """Cleanup agent manager."""
        try:
            # Cleanup any agent-specific resources
            for agent_name, agent_info in self.agents.items():
                if "cleanup" in agent_info:
                    try:
                        await agent_info["cleanup"]()
                    except Exception as e:
                        logger.warning("Agent cleanup failed", agent=agent_name, error=str(e))
            
            logger.info("Agent manager cleanup completed")
            
        except Exception as e:
            logger.error("Error during agent manager cleanup", error=str(e))
    
    async def _load_builtin_agents(self):
        """Load built-in agents."""
        try:
            # Load Claude agent
            from agents.claude_analyst_enhanced import run_claude_agent_enhanced
            self.agents["claude"] = {
                "type": "claude",
                "name": "Claude Analyst",
                "executor": run_claude_agent_enhanced,
                "capabilities": ["analysis", "reasoning", "text_generation"],
                "status": "active",
                "version": "1.0.0",
                "builtin": True
            }
            
            # Load Codex agent  
            from agents.codex_runner_enhanced import run_codex_agent_enhanced
            self.agents["codex"] = {
                "type": "codex",
                "name": "Codex Runner",
                "executor": run_codex_agent_enhanced,
                "capabilities": ["code_generation", "code_analysis", "debugging"],
                "status": "active",
                "version": "1.0.0",
                "builtin": True
            }
            
            # Load Orchestrator agent
            from agents.orchestrator_enhanced import run_orchestrator_agent_enhanced
            self.agents["orchestrator"] = {
                "type": "orchestrator",
                "name": "Task Orchestrator",
                "executor": run_orchestrator_agent_enhanced,
                "capabilities": ["task_decomposition", "workflow_management", "coordination"],
                "status": "active",
                "version": "1.0.0",
                "builtin": True
            }
            
            # Load Memory Graph agent
            from agents.memory_graph_enhanced import run_memory_graph_agent_enhanced
            self.agents["memory"] = {
                "type": "memory",
                "name": "Memory Graph Agent",
                "executor": run_memory_graph_agent_enhanced,
                "capabilities": ["memory_analysis", "graph_traversal", "pattern_recognition"],
                "status": "active",
                "version": "1.0.0",
                "builtin": True
            }
            
            logger.info("Built-in agents loaded", count=len(self.agents))
            
        except Exception as e:
            logger.error("Failed to load built-in agents", error=str(e))
            # Continue with available agents
    
    async def _load_plugin_agents(self):
        """Load plugin agents from plugins directory."""
        try:
            if not self.plugin_directory.exists():
                self.plugin_directory.mkdir(parents=True, exist_ok=True)
                logger.info("Created plugins directory")
                return
            
            # Scan for plugin manifests
            for plugin_dir in self.plugin_directory.iterdir():
                if plugin_dir.is_dir():
                    manifest_path = plugin_dir / "manifest.json"
                    if manifest_path.exists():
                        try:
                            await self._load_plugin(plugin_dir)
                        except Exception as e:
                            logger.error("Failed to load plugin", plugin=plugin_dir.name, error=str(e))
            
            logger.info("Plugin agents loaded", plugin_count=len(self.plugins))
            
        except Exception as e:
            logger.error("Failed to load plugin agents", error=str(e))
    
    async def _load_plugin(self, plugin_dir: Path):
        """Load a specific plugin."""
        manifest_path = plugin_dir / "manifest.json"
        
        # Read manifest
        import json
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
        
        manifest = PluginManifest(**manifest_data)
        
        # Validate plugin
        if not await self._validate_plugin(plugin_dir, manifest):
            raise ValueError(f"Plugin validation failed: {manifest.name}")
        
        # Load plugin module
        spec = importlib.util.spec_from_file_location(
            manifest.name,
            plugin_dir / manifest.entry_point
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get executor function
        executor = getattr(module, "execute", None)
        if not executor:
            raise ValueError(f"Plugin {manifest.name} missing execute function")
        
        # Register agent
        self.agents[manifest.agent_type] = {
            "type": manifest.agent_type,
            "name": manifest.name,
            "executor": executor,
            "capabilities": manifest.capabilities,
            "status": "active",
            "version": manifest.version,
            "builtin": False,
            "plugin_dir": plugin_dir,
            "manifest": manifest
        }
        
        self.plugins[manifest.name] = manifest
        
        logger.info("Plugin loaded", name=manifest.name, type=manifest.agent_type)
    
    async def _validate_plugin(self, plugin_dir: Path, manifest: PluginManifest) -> bool:
        """Validate plugin structure and dependencies."""
        try:
            # Check entry point exists
            entry_point_path = plugin_dir / manifest.entry_point
            if not entry_point_path.exists():
                logger.error("Plugin entry point not found", plugin=manifest.name, path=manifest.entry_point)
                return False
            
            # Check for required dependencies
            for dependency in manifest.dependencies:
                try:
                    importlib.import_module(dependency)
                except ImportError:
                    logger.error("Plugin dependency not available", plugin=manifest.name, dependency=dependency)
                    return False
            
            # Validate agent type uniqueness
            if manifest.agent_type in self.agents:
                logger.error("Agent type already exists", plugin=manifest.name, type=manifest.agent_type)
                return False
            
            return True
            
        except Exception as e:
            logger.error("Plugin validation error", plugin=manifest.name, error=str(e))
            return False
    
    async def execute_agent(self, agent_type: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent task."""
        start_time = time.time()
        
        if agent_type not in self.agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_info = self.agents[agent_type]
        
        try:
            # Add memory system to parameters
            enhanced_params = {
                **params,
                "memory_system": self.memory_system,
                "agent_manager": self
            }
            
            # Execute agent
            result = await agent_info["executor"](enhanced_params)
            
            # Update statistics
            duration_ms = (time.time() - start_time) * 1000
            stats = self.agent_stats[agent_type]
            stats["total_tasks"] += 1
            stats["successful_tasks"] += 1
            stats["total_duration_ms"] += duration_ms
            stats["last_activity"] = datetime.utcnow()
            
            # Log execution
            agent_logger.agent_complete(agent_type, params.get("session_id"), duration_ms, True)
            
            return result
            
        except Exception as e:
            # Update failure statistics
            duration_ms = (time.time() - start_time) * 1000
            stats = self.agent_stats[agent_type]
            stats["total_tasks"] += 1
            stats["failed_tasks"] += 1
            stats["total_duration_ms"] += duration_ms
            stats["last_activity"] = datetime.utcnow()
            
            # Log error
            agent_logger.agent_error(agent_type, params.get("session_id"), str(e))
            
            raise
    
    async def has_agent(self, agent_type: str) -> bool:
        """Check if agent type is available."""
        return agent_type in self.agents
    
    async def get_agent_info(self) -> List[AgentInfo]:
        """Get information about all agents."""
        agent_info_list = []
        
        for agent_type, agent_data in self.agents.items():
            stats = self.agent_stats.get(agent_type, {})
            
            agent_info_list.append(AgentInfo(
                name=agent_data["name"],
                type=agent_type,
                status=agent_data["status"],
                capabilities=agent_data["capabilities"],
                last_active=stats.get("last_activity")
            ))
        
        return agent_info_list
    
    async def get_agent_stats(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific agent."""
        if agent_type not in self.agent_stats:
            return None
        
        stats = self.agent_stats[agent_type].copy()
        
        # Calculate average duration
        if stats["total_tasks"] > 0:
            stats["average_duration_ms"] = stats["total_duration_ms"] / stats["total_tasks"]
            stats["success_rate"] = stats["successful_tasks"] / stats["total_tasks"]
        else:
            stats["average_duration_ms"] = 0.0
            stats["success_rate"] = 0.0
        
        return stats
    
    async def disable_agent(self, agent_type: str) -> bool:
        """Disable an agent."""
        if agent_type not in self.agents:
            return False
        
        self.agents[agent_type]["status"] = "disabled"
        logger.info("Agent disabled", type=agent_type)
        return True
    
    async def enable_agent(self, agent_type: str) -> bool:
        """Enable an agent."""
        if agent_type not in self.agents:
            return False
        
        self.agents[agent_type]["status"] = "active"
        logger.info("Agent enabled", type=agent_type)
        return True
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin agent."""
        try:
            # Find plugin by name
            plugin_agent_type = None
            for agent_type, agent_data in self.agents.items():
                if not agent_data.get("builtin", True) and agent_data.get("manifest", {}).name == plugin_name:
                    plugin_agent_type = agent_type
                    break
            
            if not plugin_agent_type:
                return False
            
            # Get plugin directory
            agent_data = self.agents[plugin_agent_type]
            plugin_dir = agent_data["plugin_dir"]
            
            # Remove old agent
            del self.agents[plugin_agent_type]
            del self.agent_stats[plugin_agent_type]
            if plugin_name in self.plugins:
                del self.plugins[plugin_name]
            
            # Reload plugin
            await self._load_plugin(plugin_dir)
            
            logger.info("Plugin reloaded", name=plugin_name)
            return True
            
        except Exception as e:
            logger.error("Failed to reload plugin", name=plugin_name, error=str(e))
            return False
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent types."""
        return [agent_type for agent_type, agent_data in self.agents.items() 
                if agent_data["status"] == "active"]
    
    def get_agent_capabilities(self, agent_type: str) -> List[str]:
        """Get capabilities of a specific agent."""
        if agent_type not in self.agents:
            return []
        
        return self.agents[agent_type]["capabilities"]
    
    async def create_plugin_template(self, plugin_name: str, agent_type: str) -> bool:
        """Create a plugin template for development."""
        try:
            plugin_dir = self.plugin_directory / plugin_name
            plugin_dir.mkdir(parents=True, exist_ok=True)
            
            # Create manifest
            manifest = {
                "name": plugin_name,
                "version": "1.0.0",
                "description": f"Plugin for {agent_type} agent",
                "author": "Developer",
                "agent_type": agent_type,
                "capabilities": ["custom_capability"],
                "dependencies": [],
                "entry_point": "agent.py",
                "config_schema": {}
            }
            
            with open(plugin_dir / "manifest.json", 'w') as f:
                import json
                json.dump(manifest, f, indent=2)
            
            # Create agent template
            agent_template = '''"""Plugin agent implementation."""

import asyncio
from typing import Dict, Any

async def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute agent task.
    
    Args:
        params: Task parameters including:
            - task: Task description
            - memory_system: Access to memory system
            - agent_manager: Access to agent manager
            - session_id: Session identifier
            - task_id: Task identifier
    
    Returns:
        Dict containing result and optional memory artifacts
    """
    
    # Your agent implementation here
    task = params.get("task", "Default task")
    
    # Example: Access memory system
    memory_system = params.get("memory_system")
    
    # Example: Store results in memory
    result = {
        "status": "completed",
        "message": f"Plugin {agent_type} processed: {task}",
        "data": {}
    }
    
    # Optional: Return memory artifacts to be stored
    # result["memory"] = {"key": "value"}
    
    return result


async def initialize():
    """Initialize plugin (called once on load)."""
    pass


async def cleanup():
    """Cleanup plugin resources."""
    pass
'''.replace("{agent_type}", agent_type)
            
            with open(plugin_dir / "agent.py", 'w') as f:
                f.write(agent_template)
            
            # Create README
            readme_content = f"""# {plugin_name} Plugin

## Description
Plugin for {agent_type} agent.

## Installation
1. Ensure all dependencies are installed
2. Place this directory in the plugins folder
3. Restart the application

## Configuration
Edit manifest.json to configure the plugin.

## Development
Modify agent.py to implement your agent logic.
"""
            
            with open(plugin_dir / "README.md", 'w') as f:
                f.write(readme_content)
            
            logger.info("Plugin template created", name=plugin_name, path=plugin_dir)
            return True
            
        except Exception as e:
            logger.error("Failed to create plugin template", name=plugin_name, error=str(e))
            return False