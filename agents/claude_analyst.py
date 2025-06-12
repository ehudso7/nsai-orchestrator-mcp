import os
import anthropic
from memory.graph_driver import GraphMemory
from memory.memory_cache import RedisMemory
import logging

logger = logging.getLogger(__name__)

async def run_claude_agent(params):
    task = params.get("task", "no task")
    node = params.get("node", "claude-node")
    context = params.get("context", "")
    
    # Initialize memory systems
    redis = RedisMemory()
    cache = redis.get(node) or ""
    
    # Initialize Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"result": "Anthropic API key not configured", "status": "error"}
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Build prompt with context
        prompt = f"""You are Claude, an advanced AI analyst. 
        
Task: {task}
Previous Context: {cache}
Additional Context: {context}

Provide a comprehensive analysis with actionable insights."""
        
        # Make API call to Claude
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = message.content[0].text
        
        # Store in memory
        redis.set(node, result)
        
        # Store in graph if available
        try:
            graph = GraphMemory()
            graph.insert_context(node, "ClaudeAnalysis", f"Task: {task} | Result: {result[:200]}...")
            graph.close()
        except Exception as e:
            logger.warning(f"Graph storage failed: {e}")
        
        return {
            "result": result,
            "status": "success",
            "agent": "claude",
            "model": "claude-3-sonnet"
        }
        
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return {
            "result": f"Error: {str(e)}",
            "status": "error",
            "agent": "claude"
        }
