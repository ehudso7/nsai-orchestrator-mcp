import os
import openai
from memory.graph_driver import GraphMemory
from memory.memory_cache import RedisMemory
import logging

logger = logging.getLogger(__name__)

async def run_codex_agent(params):
    task = params.get("task", "no task")
    node = params.get("node", "codex-node")
    language = params.get("language", "python")
    context = params.get("context", "")
    
    # Initialize memory
    redis = RedisMemory()
    
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"result": "OpenAI API key not configured", "status": "error"}
    
    openai.api_key = api_key
    
    try:
        # Build prompt
        prompt = f"""You are an expert code generator. Generate high-quality, production-ready code.

Task: {task}
Language: {language}
Context: {context}

Generate clean, well-commented code with best practices."""

        # Make API call to GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert programmer who writes clean, efficient code."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        
        # Store in cache
        redis.set(node, result)
        
        # Store in graph if available
        try:
            graph = GraphMemory()
            graph.insert_context(node, "CodexGeneration", f"Task: {task} | Language: {language}")
            graph.close()
        except Exception as e:
            logger.warning(f"Graph storage failed: {e}")
        
        return {
            "result": result,
            "status": "success",
            "agent": "codex",
            "model": "gpt-4",
            "language": language
        }
        
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return {
            "result": f"Error: {str(e)}",
            "status": "error",
            "agent": "codex"
        }
