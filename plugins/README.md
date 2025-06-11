# NSAI Orchestrator MCP - Plugin System

## Overview

The NSAI Orchestrator MCP supports a powerful plugin system that allows you to extend functionality with custom agents, processors, and integrations.

## Plugin Architecture

### Plugin Structure
```
plugins/
├── your-plugin/
│   ├── manifest.json          # Plugin configuration
│   ├── agent.py              # Main agent implementation
│   ├── README.md             # Plugin documentation
│   ├── requirements.txt      # Plugin dependencies (optional)
│   └── config/               # Plugin-specific configuration
│       └── schema.json
```

### Manifest Format
```json
{
  "name": "my-custom-agent",
  "version": "1.0.0",
  "description": "Custom agent for specific tasks",
  "author": "Your Name",
  "agent_type": "custom",
  "capabilities": ["custom_capability", "data_processing"],
  "dependencies": ["requests", "pandas"],
  "entry_point": "agent.py",
  "config_schema": {
    "type": "object",
    "properties": {
      "api_key": {"type": "string"},
      "endpoint": {"type": "string"}
    },
    "required": ["api_key"]
  }
}
```

## Creating a Plugin

### 1. Generate Plugin Template
```bash
mcp-cli plugin create my-custom-agent --type custom
```

### 2. Implement Agent Logic
```python
# agent.py
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
    
    # Your custom agent implementation
    task = params.get("task", "")
    memory_system = params.get("memory_system")
    
    # Process task
    result = {
        "status": "completed",
        "message": f"Processed: {task}",
        "data": {}
    }
    
    # Optional: Store results in memory
    # result["memory"] = {"key": "value"}
    
    return result


async def initialize():
    """Initialize plugin (called once on load)."""
    pass


async def cleanup():
    """Cleanup plugin resources."""
    pass
```

### 3. Configure Plugin
Edit `manifest.json` with your plugin details and dependencies.

### 4. Test Plugin
```bash
mcp-cli plugin test my-custom-agent
```

### 5. Install Plugin
```bash
mcp-cli plugin install ./plugins/my-custom-agent
```

## Plugin Types

### Agent Plugins
- Custom processing logic
- External API integrations
- Specialized analysis tools
- Data transformation pipelines

### Memory Plugins
- Custom memory storage backends
- Specialized indexing strategies
- External knowledge base integrations

### UI Plugins
- Custom dashboard components
- Specialized visualizations
- Interactive tools

## Plugin Lifecycle

1. **Discovery**: System scans plugins directory
2. **Validation**: Manifest and dependencies checked
3. **Loading**: Plugin module loaded and initialized
4. **Registration**: Agent registered with system
5. **Execution**: Plugin responds to tasks
6. **Cleanup**: Resources cleaned up on shutdown

## Security Considerations

- Plugins run in the same process as the main application
- Ensure plugin code is trusted and reviewed
- Plugin dependencies are isolated where possible
- Access to system resources is controlled

## API Reference

### Memory System Access
```python
# Insert memory node
await memory_system.insert_node(MemoryNode(
    id="custom_node_id",
    label="custom_data",
    content="Node content",
    session_id=session_id,
    tags=["custom", "plugin"]
))

# Query memory
result = await memory_system.query({
    "query_type": "search",
    "filters": {"content_contains": "search_term"}
})
```

### Agent Manager Access
```python
# Get available agents
agents = await agent_manager.get_agent_info()

# Execute another agent
result = await agent_manager.execute_agent(
    "claude", 
    "analyze", 
    {"task": "Analyze this data"}
)
```

## Best Practices

### Performance
- Use async/await for I/O operations
- Implement proper error handling
- Cache expensive operations
- Monitor resource usage

### Security
- Validate all inputs
- Never expose sensitive data
- Use secure communication protocols
- Follow principle of least privilege

### Maintainability
- Write comprehensive tests
- Document all public interfaces
- Use semantic versioning
- Provide clear error messages

## Examples

### Simple Data Processor
```python
async def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    data = params.get("data", [])
    
    # Process data
    processed = [item.upper() for item in data]
    
    return {
        "status": "completed",
        "result": processed,
        "count": len(processed)
    }
```

### External API Integration
```python
import httpx

async def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    query = params.get("query", "")
    api_key = params.get("config", {}).get("api_key")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.example.com/search",
            params={"q": query},
            headers={"Authorization": f"Bearer {api_key}"}
        )
        
        data = response.json()
    
    return {
        "status": "completed",
        "result": data,
        "memory": {
            "search_query": query,
            "results_count": len(data.get("results", []))
        }
    }
```

### Memory Analysis Plugin
```python
async def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    memory_system = params.get("memory_system")
    session_id = params.get("session_id")
    
    # Analyze memory patterns
    graph = await memory_system.get_graph({"session_id": session_id})
    
    analysis = {
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "most_connected": analyze_connections(graph),
        "topics": extract_topics(graph)
    }
    
    return {
        "status": "completed",
        "result": analysis
    }
```

## Troubleshooting

### Plugin Not Loading
1. Check manifest.json syntax
2. Verify all dependencies are installed
3. Check plugin directory permissions
4. Review logs for error messages

### Runtime Errors
1. Validate input parameters
2. Check external service availability
3. Verify configuration values
4. Monitor resource usage

### Performance Issues
1. Profile plugin execution
2. Optimize database queries
3. Cache frequently accessed data
4. Use async operations properly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your plugin
4. Add comprehensive tests
5. Submit a pull request

## Support

- Documentation: https://docs.nsai.dev/plugins
- Issues: https://github.com/nsai-team/orchestrator-mcp/issues
- Community: https://discord.gg/nsai-dev