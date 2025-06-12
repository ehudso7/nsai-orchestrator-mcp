import asyncio
import json
from typing import List, Dict, Any
from utils.llm_client import call_claude, call_openai
from agents.claude_analyst import run_claude_analyst
from agents.codex_runner import run_codex_agent
from agents.memory_graph import run_memory_graph_agent
import logging

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates multiple agents to complete complex tasks"""
    
    def __init__(self):
        self.agents = {
            "claude": run_claude_analyst,
            "codex": run_codex_agent,
            "memory": run_memory_graph_agent
        }
        
    async def decompose_task(self, task: str, available_agents: List[str]) -> Dict[str, Any]:
        """Decompose a high-level task into agent-specific subtasks"""
        
        system_prompt = f"""You are an AI task orchestrator. Break down the following task into subtasks 
        that can be handled by these specialized agents:
        
        Available agents:
        - claude: Analysis, reasoning, and text generation
        - codex: Code generation and technical implementation
        - memory: Knowledge graph queries and memory operations
        
        Task: {task}
        
        Return a JSON object with:
        {{
            "steps": [
                {{
                    "agent": "agent_name",
                    "task": "specific task description",
                    "dependencies": ["step_ids that must complete first"],
                    "id": "unique_step_id"
                }}
            ],
            "execution_order": ["ordered list of step ids"]
        }}
        """
        
        try:
            response = await call_claude(system_prompt)
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                return plan
            else:
                # Fallback to simple sequential plan
                return {
                    "steps": [
                        {
                            "agent": "claude",
                            "task": f"Analyze and plan approach for: {task}",
                            "dependencies": [],
                            "id": "step_1"
                        },
                        {
                            "agent": "codex",
                            "task": f"Implement solution based on analysis",
                            "dependencies": ["step_1"],
                            "id": "step_2"
                        }
                    ],
                    "execution_order": ["step_1", "step_2"]
                }
        except Exception as e:
            logger.error(f"Failed to decompose task: {e}")
            return {
                "steps": [{
                    "agent": "claude",
                    "task": task,
                    "dependencies": [],
                    "id": "step_1"
                }],
                "execution_order": ["step_1"]
            }
    
    async def execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step with the appropriate agent"""
        
        agent_name = step["agent"]
        task = step["task"]
        step_id = step["id"]
        
        logger.info(f"Executing step {step_id} with agent {agent_name}")
        
        if agent_name not in self.agents:
            return {
                "step_id": step_id,
                "status": "error",
                "error": f"Unknown agent: {agent_name}"
            }
        
        try:
            # Add context from previous steps
            agent_params = {
                "task": task,
                "prompt": task,
                "context": context
            }
            
            # Call the appropriate agent
            result = await self.agents[agent_name](agent_params)
            
            return {
                "step_id": step_id,
                "agent": agent_name,
                "task": task,
                "result": result,
                "status": "completed"
            }
        except Exception as e:
            logger.error(f"Step {step_id} failed: {e}")
            return {
                "step_id": step_id,
                "agent": agent_name,
                "task": task,
                "status": "error",
                "error": str(e)
            }
    
    async def execute_plan(self, plan: Dict[str, Any], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a plan with proper dependency management"""
        
        if context is None:
            context = {}
            
        results = {}
        execution_order = plan.get("execution_order", [])
        steps_by_id = {step["id"]: step for step in plan["steps"]}
        
        for step_id in execution_order:
            step = steps_by_id.get(step_id)
            if not step:
                continue
                
            # Wait for dependencies
            dependencies = step.get("dependencies", [])
            for dep_id in dependencies:
                if dep_id in results:
                    # Add dependency results to context
                    context[f"result_{dep_id}"] = results[dep_id]["result"]
            
            # Execute step
            result = await self.execute_step(step, context)
            results[step_id] = result
            
            # Update context with this step's result
            if result["status"] == "completed":
                context[f"result_{step_id}"] = result["result"]
        
        return list(results.values())
    
    async def execute_parallel(self, steps: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute multiple steps in parallel"""
        
        tasks = [self.execute_step(step, context) for step in steps]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "step_id": steps[i]["id"],
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results

async def run_orchestrator_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for the orchestrator agent"""
    
    task = params.get("task", "")
    agents = params.get("agents", ["claude", "codex"])
    context = params.get("context", {})
    execution_mode = params.get("mode", "sequential")  # sequential or parallel
    
    orchestrator = AgentOrchestrator()
    
    try:
        # Decompose the task into a plan
        plan = await orchestrator.decompose_task(task, agents)
        
        # Execute the plan
        if execution_mode == "parallel":
            # Group steps that can run in parallel
            parallel_groups = []
            current_group = []
            
            for step_id in plan["execution_order"]:
                step = next(s for s in plan["steps"] if s["id"] == step_id)
                if not step.get("dependencies"):
                    current_group.append(step)
                else:
                    if current_group:
                        parallel_groups.append(current_group)
                        current_group = []
                    parallel_groups.append([step])
            
            if current_group:
                parallel_groups.append(current_group)
            
            # Execute groups
            all_results = []
            for group in parallel_groups:
                if len(group) > 1:
                    results = await orchestrator.execute_parallel(group, context)
                else:
                    results = [await orchestrator.execute_step(group[0], context)]
                all_results.extend(results)
                
                # Update context with results
                for result in results:
                    if result["status"] == "completed":
                        context[f"result_{result['step_id']}"] = result["result"]
            
            execution_results = all_results
        else:
            # Sequential execution
            execution_results = await orchestrator.execute_plan(plan, context)
        
        # Synthesize final result
        synthesis_prompt = f"""Based on the following execution results, provide a comprehensive summary:
        
        Task: {task}
        
        Results:
        {json.dumps(execution_results, indent=2)}
        
        Provide a clear, actionable summary of what was accomplished.
        """
        
        final_summary = await call_claude(synthesis_prompt)
        
        return {
            "status": "completed",
            "task": task,
            "plan": plan,
            "results": execution_results,
            "summary": final_summary,
            "agents_used": list(set(r["agent"] for r in execution_results if "agent" in r))
        }
        
    except Exception as e:
        logger.error(f"Orchestrator failed: {e}")
        return {
            "status": "error",
            "task": task,
            "error": str(e)
        }