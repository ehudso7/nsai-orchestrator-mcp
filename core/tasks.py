from celery import Task
from celery.exceptions import SoftTimeLimitExceeded
from core.celery_app import celery_app
from core.database import SessionLocal
from core.models import WorkflowExecution, AgentExecution, Workflow, User, ExecutionStatus
from agents.claude_analyst import run_claude_analyst
from agents.codex_runner import run_codex_agent
from agents.orchestrator_agent import run_orchestrator_agent
from agents.memory_graph import run_memory_agent
from agents.web_scraper import run_web_scraper_agent
from agents.data_analyzer import run_data_analyzer_agent
from datetime import datetime, timedelta
import json
import asyncio
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class BaseTask(Task):
    """Base task with automatic session management"""
    
    def __call__(self, *args, **kwargs):
        with SessionLocal() as db:
            self.db = db
            try:
                return self.run(*args, **kwargs)
            except Exception as e:
                db.rollback()
                raise
            finally:
                db.close()

@celery_app.task(bind=True, base=BaseTask, max_retries=3)
def execute_workflow_async(self, workflow_id: int, user_id: int, input_data: Dict[str, Any]):
    """Execute a workflow asynchronously"""
    
    try:
        # Get workflow and create execution record
        workflow = self.db.query(Workflow).filter_by(id=workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            user_id=user_id,
            input_data=input_data,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.utcnow(),
            execution_log=[{"timestamp": datetime.utcnow().isoformat(), "message": "Workflow execution started"}]
        )
        self.db.add(execution)
        self.db.commit()
        
        # Parse workflow definition
        nodes = workflow.nodes
        edges = workflow.edges
        
        # Execute nodes in topological order
        results = {}
        for node in nodes:
            if node["type"] == "agent":
                # Execute agent node
                agent_result = execute_agent_node(
                    self.db,
                    execution.id,
                    node,
                    results,
                    input_data
                )
                results[node["id"]] = agent_result
        
        # Update execution status
        execution.status = ExecutionStatus.COMPLETED
        execution.completed_at = datetime.utcnow()
        execution.duration_ms = int((execution.completed_at - execution.started_at).total_seconds() * 1000)
        execution.output_data = results
        
        # Update workflow metrics
        workflow.total_executions += 1
        workflow.last_executed_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "execution_id": execution.uuid,
            "status": "completed",
            "results": results
        }
        
    except SoftTimeLimitExceeded:
        logger.error(f"Workflow execution {workflow_id} exceeded time limit")
        if execution:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = "Execution time limit exceeded"
            self.db.commit()
        raise
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        if execution:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            self.db.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

def execute_agent_node(db, execution_id: int, node: Dict[str, Any], 
                      previous_results: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single agent node"""
    
    agent_type = node["data"].get("agent")
    task = node["data"].get("task", "")
    
    # Create agent execution record
    agent_execution = AgentExecution(
        workflow_execution_id=execution_id,
        agent_type=agent_type,
        node_id=node["id"],
        status=ExecutionStatus.RUNNING,
        started_at=datetime.utcnow(),
        input_data={"task": task, "context": previous_results}
    )
    db.add(agent_execution)
    db.commit()
    
    try:
        # Prepare agent parameters
        params = {
            "task": task,
            "prompt": task,
            "context": previous_results,
            "input_data": input_data
        }
        
        # Execute appropriate agent
        if agent_type == "claude":
            result = asyncio.run(run_claude_analyst(params))
        elif agent_type == "codex":
            result = asyncio.run(run_codex_agent(params))
        elif agent_type == "orchestrator":
            result = asyncio.run(run_orchestrator_agent(params))
        elif agent_type == "memory":
            result = asyncio.run(run_memory_agent(params))
        elif agent_type == "webscraper":
            result = asyncio.run(run_web_scraper_agent(params))
        elif agent_type == "dataanalyzer":
            result = asyncio.run(run_data_analyzer_agent(params))
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Update execution record
        agent_execution.status = ExecutionStatus.COMPLETED
        agent_execution.completed_at = datetime.utcnow()
        agent_execution.duration_ms = int((agent_execution.completed_at - agent_execution.started_at).total_seconds() * 1000)
        agent_execution.output_data = result
        
        db.commit()
        return result
        
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        agent_execution.status = ExecutionStatus.FAILED
        agent_execution.error_message = str(e)
        agent_execution.completed_at = datetime.utcnow()
        db.commit()
        raise

@celery_app.task(bind=True, base=BaseTask)
def execute_agent_async(self, agent_type: str, params: Dict[str, Any], user_id: int):
    """Execute a single agent asynchronously"""
    
    try:
        # Track API usage
        user = self.db.query(User).filter_by(id=user_id).first()
        if user:
            user.api_calls_count += 1
            self.db.commit()
        
        # Execute agent based on type
        if agent_type == "claude":
            result = asyncio.run(run_claude_analyst(params))
        elif agent_type == "codex":
            result = asyncio.run(run_codex_agent(params))
        elif agent_type == "orchestrator":
            result = asyncio.run(run_orchestrator_agent(params))
        elif agent_type == "memory":
            result = asyncio.run(run_memory_agent(params))
        elif agent_type == "webscraper":
            result = asyncio.run(run_web_scraper_agent(params))
        elif agent_type == "dataanalyzer":
            result = asyncio.run(run_data_analyzer_agent(params))
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return result
        
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise self.retry(exc=e, countdown=60)

@celery_app.task(bind=True, base=BaseTask)
def cleanup_old_executions(self):
    """Clean up old workflow executions"""
    
    try:
        # Delete executions older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_executions = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.created_at < cutoff_date
        ).all()
        
        count = len(old_executions)
        for execution in old_executions:
            self.db.delete(execution)
        
        self.db.commit()
        logger.info(f"Cleaned up {count} old executions")
        
        return {"deleted_count": count}
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise

@celery_app.task(bind=True, base=BaseTask)
def update_workflow_metrics(self):
    """Update workflow performance metrics"""
    
    try:
        workflows = self.db.query(Workflow).all()
        
        for workflow in workflows:
            # Calculate metrics from recent executions
            recent_executions = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.workflow_id == workflow.id,
                WorkflowExecution.completed_at.isnot(None)
            ).order_by(WorkflowExecution.completed_at.desc()).limit(100).all()
            
            if recent_executions:
                # Calculate average execution time
                total_time = sum(e.duration_ms for e in recent_executions if e.duration_ms)
                workflow.avg_execution_time_ms = total_time / len(recent_executions) if recent_executions else 0
                
                # Calculate success rate
                successful = sum(1 for e in recent_executions if e.status == ExecutionStatus.COMPLETED)
                workflow.success_rate = (successful / len(recent_executions)) * 100
        
        self.db.commit()
        logger.info(f"Updated metrics for {len(workflows)} workflows")
        
        return {"updated_count": len(workflows)}
        
    except Exception as e:
        logger.error(f"Metrics update failed: {e}")
        raise

@celery_app.task(bind=True, base=BaseTask)
def check_api_key_expiration(self):
    """Check and notify about expiring API keys"""
    
    try:
        from core.models import ApiKey
        
        # Find keys expiring in next 7 days
        expiry_threshold = datetime.utcnow() + timedelta(days=7)
        
        expiring_keys = self.db.query(ApiKey).filter(
            ApiKey.expires_at <= expiry_threshold,
            ApiKey.is_active == True
        ).all()
        
        notifications = []
        for key in expiring_keys:
            # Here you would send notification to user
            # For now, just log it
            logger.warning(f"API key {key.key_prefix} for user {key.user_id} expires on {key.expires_at}")
            notifications.append({
                "user_id": key.user_id,
                "key_prefix": key.key_prefix,
                "expires_at": key.expires_at.isoformat()
            })
        
        return {"expiring_keys": len(notifications), "notifications": notifications}
        
    except Exception as e:
        logger.error(f"API key check failed: {e}")
        raise

@celery_app.task(bind=True)
def analyze_data_async(self, file_path: str, analysis_type: str, user_id: int):
    """Analyze data file asynchronously"""
    
    try:
        params = {
            "file_path": file_path,
            "analysis_type": analysis_type
        }
        
        result = asyncio.run(run_data_analyzer_agent(params))
        
        # Store results in cache for retrieval
        from core.redis_config import redis_manager
        if redis_manager.redis_client:
            cache_key = f"analysis_result:{user_id}:{self.request.id}"
            asyncio.run(redis_manager.redis_client.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(result)
            ))
        
        return {
            "task_id": self.request.id,
            "status": "completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Data analysis failed: {e}")
        raise self.retry(exc=e, countdown=60)

@celery_app.task(bind=True)
def scrape_web_async(self, urls: List[str], extract_rules: Dict[str, Any], user_id: int):
    """Scrape multiple URLs asynchronously"""
    
    try:
        params = {
            "urls": urls,
            "extract_rules": extract_rules,
            "mode": "multiple"
        }
        
        result = asyncio.run(run_web_scraper_agent(params))
        
        # Store results
        from core.redis_config import redis_manager
        if redis_manager.redis_client:
            cache_key = f"scraping_result:{user_id}:{self.request.id}"
            asyncio.run(redis_manager.redis_client.setex(
                cache_key,
                3600,
                json.dumps(result)
            ))
        
        return {
            "task_id": self.request.id,
            "status": "completed",
            "urls_scraped": len(urls),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Web scraping failed: {e}")
        raise self.retry(exc=e, countdown=60)