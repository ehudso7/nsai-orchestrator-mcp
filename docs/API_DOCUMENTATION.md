# NSAI Orchestrator API Documentation

## Overview

The NSAI Orchestrator API provides programmatic access to our world-class multi-agent orchestration platform. Built on REST principles with WebSocket support for real-time features.

### Base URL
```
https://api.nsai-orchestrator.com/v1
```

### Authentication

All API requests require authentication using Bearer tokens:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     https://api.nsai-orchestrator.com/v1/agents
```

## Core Endpoints

### Agents

#### List Available Agents
```http
GET /agents
```

**Response:**
```json
{
  "agents": [
    {
      "id": "claude-3",
      "name": "Claude 3",
      "type": "language_model",
      "capabilities": ["text_generation", "analysis", "coding"],
      "status": "online",
      "performance": {
        "avg_response_time": 245,
        "success_rate": 0.997,
        "tasks_completed": 1548293
      }
    },
    {
      "id": "codex-1",
      "name": "Codex",
      "type": "code_model",
      "capabilities": ["code_generation", "debugging", "refactoring"],
      "status": "online"
    }
  ]
}
```

#### Execute Task
```http
POST /agents/{agent_id}/execute
```

**Request:**
```json
{
  "task": {
    "type": "analysis",
    "prompt": "Analyze customer sentiment in the provided feedback",
    "data": {
      "feedback": ["Great product!", "Needs improvement", "Excellent service"]
    },
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 1000,
      "timeout": 30000
    }
  },
  "priority": "high",
  "callback_url": "https://your-app.com/webhook"
}
```

**Response:**
```json
{
  "task_id": "tsk_1234567890",
  "status": "processing",
  "agent": "claude-3",
  "created_at": "2024-01-10T10:30:00Z",
  "estimated_completion": "2024-01-10T10:30:30Z",
  "tracking_url": "wss://api.nsai-orchestrator.com/v1/tasks/tsk_1234567890/stream"
}
```

### Workflows

#### Create Workflow
```http
POST /workflows
```

**Request:**
```json
{
  "name": "Customer Support Pipeline",
  "description": "Automated customer inquiry processing",
  "nodes": [
    {
      "id": "classify",
      "type": "agent",
      "agent_id": "claude-3",
      "task": {
        "type": "classification",
        "prompt": "Classify the customer inquiry type"
      }
    },
    {
      "id": "respond",
      "type": "agent", 
      "agent_id": "claude-3",
      "task": {
        "type": "generation",
        "prompt": "Generate appropriate response based on classification"
      },
      "depends_on": ["classify"]
    }
  ],
  "trigger": {
    "type": "webhook",
    "config": {
      "endpoint": "/webhooks/customer-support"
    }
  }
}
```

#### Execute Workflow
```http
POST /workflows/{workflow_id}/execute
```

**Request:**
```json
{
  "input": {
    "customer_message": "I can't log into my account",
    "customer_id": "cust_123",
    "priority": "high"
  },
  "execution_mode": "parallel_where_possible"
}
```

### Memory & Context

#### Store Context
```http
POST /memory/contexts
```

**Request:**
```json
{
  "namespace": "customer_support",
  "key": "cust_123_history",
  "data": {
    "interactions": [
      {
        "timestamp": "2024-01-10T09:00:00Z",
        "type": "support_ticket",
        "resolved": true
      }
    ],
    "preferences": {
      "communication": "email",
      "language": "en"
    }
  },
  "ttl": 2592000
}
```

#### Retrieve Context
```http
GET /memory/contexts/{namespace}/{key}
```

**Response:**
```json
{
  "namespace": "customer_support",
  "key": "cust_123_history",
  "data": {
    "interactions": [...],
    "preferences": {...}
  },
  "created_at": "2024-01-10T09:00:00Z",
  "expires_at": "2024-02-09T09:00:00Z"
}
```

### Real-time Monitoring

#### Get System Metrics
```http
GET /metrics
```

**Response:**
```json
{
  "timestamp": "2024-01-10T10:30:00Z",
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "active_tasks": 127,
    "queued_tasks": 15
  },
  "agents": {
    "claude-3": {
      "status": "healthy",
      "active_tasks": 45,
      "avg_response_time": 243,
      "error_rate": 0.001
    }
  },
  "performance": {
    "requests_per_second": 1247,
    "p95_latency": 98,
    "p99_latency": 145,
    "cache_hit_rate": 0.94
  }
}
```

## WebSocket API

### Real-time Task Monitoring
```javascript
const ws = new WebSocket('wss://api.nsai-orchestrator.com/v1/tasks/tsk_1234567890/stream');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Task update:', update);
  // {
  //   "type": "progress",
  //   "task_id": "tsk_1234567890",
  //   "progress": 0.75,
  //   "message": "Analyzing data...",
  //   "timestamp": "2024-01-10T10:30:15Z"
  // }
};
```

### Live Metrics Stream
```javascript
const metrics = new WebSocket('wss://api.nsai-orchestrator.com/v1/metrics/stream');

metrics.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateDashboard(data);
  // Real-time system metrics updated every second
};
```

## Advanced Features

### Batch Operations
```http
POST /batch
```

**Request:**
```json
{
  "operations": [
    {
      "method": "POST",
      "path": "/agents/claude-3/execute",
      "body": { "task": {...} }
    },
    {
      "method": "GET",
      "path": "/memory/contexts/customer/cust_123"
    }
  ],
  "parallel": true
}
```

### Circuit Breaker Status
```http
GET /health/circuit-breakers
```

**Response:**
```json
{
  "circuit_breakers": {
    "claude-3": {
      "state": "closed",
      "failure_count": 2,
      "success_count": 9847,
      "last_failure": "2024-01-10T08:15:00Z"
    },
    "external_api": {
      "state": "half_open",
      "failure_count": 5,
      "next_attempt": "2024-01-10T10:35:00Z"
    }
  }
}
```

## Error Handling

All errors follow RFC 7807 (Problem Details):

```json
{
  "type": "https://api.nsai-orchestrator.com/errors/rate-limit-exceeded",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "API rate limit of 1000 requests per minute exceeded",
  "instance": "/agents/claude-3/execute",
  "rate_limit": {
    "limit": 1000,
    "remaining": 0,
    "reset": "2024-01-10T10:31:00Z"
  }
}
```

## Rate Limiting

| Tier | Requests/Minute | Requests/Day | Burst |
|------|----------------|--------------|-------|
| Free | 60 | 1,000 | 10 |
| Starter | 300 | 10,000 | 50 |
| Professional | 1,000 | 100,000 | 200 |
| Enterprise | Unlimited | Unlimited | Custom |

## SDKs

Official SDKs available for:

### Python
```python
from nsai_orchestrator import Client

client = Client(api_key="YOUR_API_KEY")

# Execute task
result = await client.agents.execute(
    agent_id="claude-3",
    task={
        "type": "analysis",
        "prompt": "Analyze this data",
        "data": {"sales": [100, 200, 300]}
    }
)

# Create workflow
workflow = await client.workflows.create(
    name="My Workflow",
    nodes=[...]
)
```

### Node.js
```javascript
import { NSAIOrchestrator } from '@nsai/orchestrator-sdk';

const client = new NSAIOrchestrator({ apiKey: 'YOUR_API_KEY' });

// Execute task
const result = await client.agents.execute('claude-3', {
  task: {
    type: 'analysis',
    prompt: 'Analyze this data',
    data: { sales: [100, 200, 300] }
  }
});

// Stream results
const stream = await client.tasks.stream(result.taskId);
stream.on('progress', (update) => {
  console.log(`Progress: ${update.progress * 100}%`);
});
```

### Go
```go
import "github.com/nsai/orchestrator-go"

client := orchestrator.NewClient("YOUR_API_KEY")

// Execute task
result, err := client.Agents.Execute(context.Background(), &orchestrator.ExecuteRequest{
    AgentID: "claude-3",
    Task: orchestrator.Task{
        Type: "analysis",
        Prompt: "Analyze this data",
    },
})
```

## Webhooks

Configure webhooks to receive real-time updates:

```http
POST /webhooks
```

**Request:**
```json
{
  "url": "https://your-app.com/nsai-webhook",
  "events": ["task.completed", "task.failed", "workflow.completed"],
  "secret": "your-webhook-secret"
}
```

Webhook payload:
```json
{
  "event": "task.completed",
  "timestamp": "2024-01-10T10:30:45Z",
  "data": {
    "task_id": "tsk_1234567890",
    "agent": "claude-3",
    "duration": 2450,
    "result": {...}
  },
  "signature": "sha256=abcdef..."
}
```

## Best Practices

### 1. Use Idempotency Keys
```bash
curl -H "Idempotency-Key: unique-request-id" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -X POST https://api.nsai-orchestrator.com/v1/agents/claude-3/execute
```

### 2. Implement Exponential Backoff
```python
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

### 3. Use Batch Operations
Instead of:
```python
# Inefficient
for item in items:
    await client.agents.execute("claude-3", process_item(item))
```

Do:
```python
# Efficient
await client.batch.execute([
    {"method": "POST", "path": f"/agents/claude-3/execute", "body": process_item(item)}
    for item in items
])
```

### 4. Stream Large Responses
```python
# For large results, use streaming
async with client.agents.execute_stream("claude-3", large_task) as stream:
    async for chunk in stream:
        process_chunk(chunk)
```

## Changelog

### v1.5.0 (Latest)
- Added visual workflow builder API
- Improved response times by 40%
- New batch operations endpoint
- WebSocket connection pooling

### v1.4.0
- Multi-region support
- Circuit breaker status endpoint
- Enhanced error messages
- SDK performance improvements

---

For more examples and use cases, visit our [Developer Portal](https://developers.nsai-orchestrator.com).