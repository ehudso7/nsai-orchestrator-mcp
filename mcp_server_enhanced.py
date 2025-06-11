"""Enhanced MCP Server with production-grade features."""

import asyncio
import uuid
import time
from typing import Dict, Callable, Any, Optional, List
from datetime import datetime, timedelta

import structlog
from config import get_settings
from core.logging import agent_logger, performance_logger
from core.metrics import metrics_collector
from memory.enhanced_memory import EnhancedMemorySystem
from agents.enhanced_agents import AgentManager
from schemas import MemoryNode, MemoryGraph, AgentInfo

logger = structlog.get_logger()
settings = get_settings()


class MCPServerEnhanced:
    """Enhanced MCP Server with advanced memory, monitoring, and agent management."""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.agent_manager = None
        self.memory_system = None
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_history: List[Dict[str, Any]] = []
        self.websocket_manager = None
        
        logger.info("Initializing Enhanced MCP Server", session_id=self.session_id)
    
    async def start(self):
        """Start the enhanced MCP server."""
        try:
            # Initialize memory system
            self.memory_system = EnhancedMemorySystem()
            await self.memory_system.initialize()
            
            # Initialize agent manager
            self.agent_manager = AgentManager(self.memory_system)
            await self.agent_manager.initialize()
            
            # Start background tasks
            asyncio.create_task(self._cleanup_expired_tasks())
            asyncio.create_task(self._memory_maintenance())
            
            logger.info("Enhanced MCP Server started successfully", session_id=self.session_id)
            
        except Exception as e:
            logger.error("Failed to start Enhanced MCP Server", error=str(e))
            raise
    
    async def stop(self):
        """Stop the enhanced MCP server."""
        try:
            # Cancel active tasks
            for task_id in list(self.active_tasks.keys()):
                await self._cancel_task(task_id)
            
            # Cleanup memory system
            if self.memory_system:
                await self.memory_system.cleanup()
            
            # Cleanup agent manager
            if self.agent_manager:
                await self.agent_manager.cleanup()
            
            logger.info("Enhanced MCP Server stopped", session_id=self.session_id)
            
        except Exception as e:
            logger.error("Error stopping Enhanced MCP Server", error=str(e))
    
    async def handle_rpc(self, payload: dict) -> dict:
        """Handle RPC requests with enhanced features."""
        task_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            method = payload.get("method")
            params = payload.get("params", {})
            agent_type = params.get("agent")
            
            # Validate input
            if not method:
                raise ValueError("Method is required")
            
            if not agent_type:
                raise ValueError("Agent parameter is required")
            
            # Create task record
            task_record = {
                "task_id": task_id,
                "method": method,
                "agent_type": agent_type,
                "params": params,
                "start_time": start_time,
                "status": "running",
                "session_id": self.session_id
            }
            
            self.active_tasks[task_id] = task_record
            
            # Log task start
            agent_logger.agent_start(agent_type, self.session_id, method)
            
            # Execute task
            result = await self._execute_task(method, params, task_id)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Update task record
            task_record.update({
                "status": "completed",
                "result": result,
                "duration_ms": duration_ms,
                "end_time": time.time()
            })
            
            # Move to history and remove from active
            self.task_history.append(task_record)
            del self.active_tasks[task_id]
            
            # Log completion
            agent_logger.agent_complete(agent_type, self.session_id, duration_ms, True)
            
            # Record metrics
            metrics_collector.record_agent_task(agent_type, "success", duration_ms / 1000)
            
            return {
                "success": True,
                "result": result,
                "task_id": task_id,
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Update task record for failure
            if task_id in self.active_tasks:
                self.active_tasks[task_id].update({
                    "status": "failed",
                    "error": str(e),
                    "duration_ms": duration_ms,
                    "end_time": time.time()
                })
                
                # Move to history
                self.task_history.append(self.active_tasks[task_id])
                del self.active_tasks[task_id]
            
            # Log error
            agent_type = payload.get("params", {}).get("agent", "unknown")
            agent_logger.agent_error(agent_type, self.session_id, str(e))
            
            # Record metrics
            metrics_collector.record_agent_task(agent_type, "error", duration_ms / 1000)
            
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id,
                "duration_ms": duration_ms
            }
    
    async def _execute_task(self, method: str, params: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """Execute a task with the appropriate agent."""
        agent_type = params.get("agent")
        
        # Check if agent exists
        if not await self.agent_manager.has_agent(agent_type):
            raise ValueError(f"Unknown agent: {agent_type}")
        
        # Add task context to params
        enhanced_params = {
            **params,
            "task_id": task_id,
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Execute with the agent
        result = await self.agent_manager.execute_agent(agent_type, method, enhanced_params)
        
        # Store memory if agent produced memory artifacts
        if "memory" in result:
            await self._store_task_memory(agent_type, task_id, result["memory"])
        
        return result
    
    async def _store_task_memory(self, agent_type: str, task_id: str, memory_data: Dict[str, Any]):
        """Store memory artifacts from task execution."""
        try:
            node_id = f"{agent_type}_{task_id}_{int(time.time())}"
            
            # Create memory node
            memory_node = MemoryNode(
                id=node_id,
                label=f"{agent_type}_result",
                content=str(memory_data),
                session_id=self.session_id,
                tags=[agent_type, "task_result", task_id]
            )
            
            # Store in memory system
            await self.memory_system.insert_node(memory_node)
            
            # Log memory insertion
            agent_logger.memory_insert(
                agent_type=agent_type,
                session_id=self.session_id,
                node_id=node_id,
                memory_type="task_result"
            )
            
        except Exception as e:
            logger.error("Failed to store task memory", error=str(e), task_id=task_id)
    
    async def get_memory_graph(self, filters: Optional[Dict[str, Any]] = None) -> MemoryGraph:
        """Get memory graph visualization data."""
        try:
            return await self.memory_system.get_graph(filters)
        except Exception as e:
            logger.error("Failed to get memory graph", error=str(e))
            raise
    
    async def query_memory(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Query the memory system."""
        try:
            return await self.memory_system.query(query)
        except Exception as e:
            logger.error("Memory query failed", error=str(e))
            raise
    
    async def get_agent_info(self) -> List[AgentInfo]:
        """Get information about available agents."""
        try:
            return await self.agent_manager.get_agent_info()
        except Exception as e:
            logger.error("Failed to get agent info", error=str(e))
            raise
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check task history
        for task in self.task_history:
            if task["task_id"] == task_id:
                return task
        
        return None
    
    async def get_session_tasks(self) -> Dict[str, Any]:
        """Get all tasks for current session."""
        return {
            "session_id": self.session_id,
            "active_tasks": list(self.active_tasks.values()),
            "completed_tasks": [t for t in self.task_history if t.get("session_id") == self.session_id],
            "total_active": len(self.active_tasks),
            "total_completed": len([t for t in self.task_history if t.get("session_id") == self.session_id])
        }
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel an active task."""
        return await self._cancel_task(task_id)
    
    async def _cancel_task(self, task_id: str) -> bool:
        """Internal method to cancel a task."""
        if task_id not in self.active_tasks:
            return False
        
        try:
            # Update task status
            task_record = self.active_tasks[task_id]
            task_record.update({
                "status": "cancelled",
                "end_time": time.time(),
                "duration_ms": (time.time() - task_record["start_time"]) * 1000
            })
            
            # Move to history
            self.task_history.append(task_record)
            del self.active_tasks[task_id]
            
            logger.info("Task cancelled", task_id=task_id)
            return True
            
        except Exception as e:
            logger.error("Failed to cancel task", task_id=task_id, error=str(e))
            return False
    
    async def _cleanup_expired_tasks(self):
        """Background task to cleanup expired tasks."""
        while True:
            try:
                current_time = time.time()
                expired_tasks = []
                
                # Find tasks running longer than 5 minutes
                for task_id, task_record in self.active_tasks.items():
                    if current_time - task_record["start_time"] > 300:  # 5 minutes
                        expired_tasks.append(task_id)
                
                # Cancel expired tasks
                for task_id in expired_tasks:
                    await self._cancel_task(task_id)
                    logger.warning("Task expired and cancelled", task_id=task_id)
                
                # Cleanup old task history (keep last 1000 tasks)
                if len(self.task_history) > 1000:
                    self.task_history = self.task_history[-1000:]
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error("Error in task cleanup", error=str(e))
                await asyncio.sleep(60)
    
    async def _memory_maintenance(self):
        """Background task for memory system maintenance."""
        while True:
            try:
                # Trigger memory system maintenance
                if self.memory_system:
                    await self.memory_system.maintenance()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error("Error in memory maintenance", error=str(e))
                await asyncio.sleep(300)
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        uptime = time.time() - self.start_time
        
        return {
            "session_id": self.session_id,
            "uptime_seconds": uptime,
            "active_tasks": len(self.active_tasks),
            "total_tasks_executed": len(self.task_history),
            "memory_nodes": self.memory_system.get_node_count() if self.memory_system else 0,
            "available_agents": len(self.agent_manager.agents) if self.agent_manager else 0,
            "server_start_time": self.start_time
        }