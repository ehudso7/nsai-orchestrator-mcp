"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { motion, AnimatePresence, useAnimation } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { io, Socket } from "socket.io-client";
import { 
  Activity, 
  AlertCircle, 
  CheckCircle, 
  Cpu, 
  Database, 
  Loader2, 
  MemoryStick,
  Network,
  Play,
  RefreshCw,
  Settings,
  Sparkles,
  Terminal,
  Zap,
  Brain,
  Code,
  FileCode2,
  Gauge,
  Globe,
  Lock,
  Monitor,
  Shield,
  Workflow
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn, formatBytes, formatDuration, getRelativeTime, getStatusColor } from "@/lib/utils";
import { toast } from "sonner";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

// Enhanced Types
interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_used: number;
  memory_total: number;
  disk_percent: number;
  network_in: number;
  network_out: number;
  active_connections: number;
  requests_per_second: number;
  average_response_time: number;
  error_rate: number;
  cache_hit_rate: number;
}

interface AgentStatus {
  id: string;
  name: string;
  status: "idle" | "running" | "error" | "offline";
  last_active: Date;
  tasks_completed: number;
  tasks_failed: number;
  average_duration: number;
  current_task?: string;
  capabilities: string[];
  performance_score: number;
}

interface TaskResult {
  id: string;
  agent: string;
  task: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  result?: any;
  error?: string;
  started_at: Date;
  completed_at?: Date;
  duration?: number;
  retries: number;
  logs: LogEntry[];
}

interface LogEntry {
  timestamp: Date;
  level: "info" | "warning" | "error" | "debug";
  message: string;
  metadata?: any;
}

interface WorkflowNode {
  id: string;
  type: "agent" | "condition" | "parallel" | "sequential";
  agent?: string;
  task?: string;
  connections: string[];
  position: { x: number; y: number };
}

// Custom Hooks
const useWebSocket = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const socketInstance = io(WS_URL, {
      transports: ["websocket"],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    socketInstance.on("connect", () => {
      setConnected(true);
      toast.success("Real-time connection established");
    });

    socketInstance.on("disconnect", () => {
      setConnected(false);
      toast.error("Real-time connection lost");
    });

    socketInstance.on("error", (error) => {
      console.error("WebSocket error:", error);
      toast.error("Connection error occurred");
    });

    setSocket(socketInstance);

    return () => {
      socketInstance.disconnect();
    };
  }, []);

  return { socket, connected };
};

const useSystemMetrics = () => {
  return useQuery({
    queryKey: ["systemMetrics"],
    queryFn: async (): Promise<SystemMetrics> => {
      const response = await fetch(`${API_URL}/api/metrics`);
      if (!response.ok) throw new Error("Failed to fetch metrics");
      return response.json();
    },
    refetchInterval: 2000, // Real-time metrics
  });
};

const useAgents = () => {
  return useQuery({
    queryKey: ["agents"],
    queryFn: async (): Promise<AgentStatus[]> => {
      const response = await fetch(`${API_URL}/api/agents`);
      if (!response.ok) throw new Error("Failed to fetch agents");
      return response.json();
    },
    refetchInterval: 5000,
  });
};

// Enhanced UI Components
const MetricCard = ({ 
  icon: Icon, 
  label, 
  value, 
  unit, 
  trend, 
  status = "normal" 
}: {
  icon: any;
  label: string;
  value: number | string;
  unit?: string;
  trend?: number;
  status?: "normal" | "warning" | "critical";
}) => {
  const controls = useAnimation();
  
  useEffect(() => {
    controls.start({
      scale: [1, 1.05, 1],
      transition: { duration: 0.3 }
    });
  }, [value]);

  return (
    <motion.div
      animate={controls}
      className={cn(
        "relative overflow-hidden rounded-xl border bg-gradient-to-br p-6 shadow-sm transition-all hover:shadow-lg",
        status === "critical" && "border-red-500 from-red-50 to-red-100 dark:from-red-950 dark:to-red-900",
        status === "warning" && "border-yellow-500 from-yellow-50 to-yellow-100 dark:from-yellow-950 dark:to-yellow-900",
        status === "normal" && "border-gray-200 from-white to-gray-50 dark:border-gray-800 dark:from-gray-950 dark:to-gray-900"
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{label}</p>
          <p className="mt-2 flex items-baseline gap-1">
            <span className="text-3xl font-bold tracking-tight">{value}</span>
            {unit && <span className="text-sm text-gray-500">{unit}</span>}
          </p>
          {trend !== undefined && (
            <p className={cn(
              "mt-1 text-xs font-medium",
              trend > 0 ? "text-green-600" : "text-red-600"
            )}>
              {trend > 0 ? "+" : ""}{trend}% from last hour
            </p>
          )}
        </div>
        <div className={cn(
          "rounded-lg p-3",
          status === "critical" && "bg-red-500 text-white",
          status === "warning" && "bg-yellow-500 text-white",
          status === "normal" && "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
        )}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      
      {/* Animated background pattern */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />
      </div>
    </motion.div>
  );
};

const AgentCard = ({ agent, onExecute }: { agent: AgentStatus; onExecute: (agent: string) => void }) => {
  const statusColors = {
    idle: "bg-gray-500",
    running: "bg-blue-500 animate-pulse",
    error: "bg-red-500",
    offline: "bg-gray-400"
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="group relative overflow-hidden rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:shadow-xl dark:border-gray-800 dark:bg-gray-950"
    >
      {/* Status indicator */}
      <div className="absolute right-4 top-4">
        <div className="relative">
          <div className={cn("h-3 w-3 rounded-full", statusColors[agent.status])} />
          {agent.status === "running" && (
            <div className={cn("absolute inset-0 h-3 w-3 animate-ping rounded-full", statusColors[agent.status])} />
          )}
        </div>
      </div>

      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 text-white">
          {agent.name === "Claude" ? <Brain className="h-6 w-6" /> : <Code className="h-6 w-6" />}
        </div>
        <div>
          <h3 className="text-lg font-semibold">{agent.name}</h3>
          <p className="text-sm text-gray-500">
            {agent.current_task || `Last active ${getRelativeTime(new Date(agent.last_active))}`}
          </p>
        </div>
      </div>

      <div className="mb-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-500">Success Rate</p>
          <p className="font-semibold">
            {agent.tasks_completed > 0 
              ? `${((agent.tasks_completed / (agent.tasks_completed + agent.tasks_failed)) * 100).toFixed(1)}%`
              : "N/A"
            }
          </p>
        </div>
        <div>
          <p className="text-gray-500">Avg Duration</p>
          <p className="font-semibold">{formatDuration(agent.average_duration)}</p>
        </div>
        <div>
          <p className="text-gray-500">Tasks</p>
          <p className="font-semibold">{agent.tasks_completed}</p>
        </div>
        <div>
          <p className="text-gray-500">Performance</p>
          <p className="font-semibold">{agent.performance_score.toFixed(1)}/10</p>
        </div>
      </div>

      <div className="mb-4">
        <p className="mb-2 text-sm font-medium text-gray-500">Capabilities</p>
        <div className="flex flex-wrap gap-1">
          {agent.capabilities.map((cap) => (
            <span
              key={cap}
              className="rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400"
            >
              {cap}
            </span>
          ))}
        </div>
      </div>

      <Button
        variant="gradient"
        className="w-full"
        disabled={agent.status !== "idle"}
        onClick={() => onExecute(agent.id)}
      >
        {agent.status === "running" ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Processing...
          </>
        ) : (
          <>
            <Play className="mr-2 h-4 w-4" />
            Execute Task
          </>
        )}
      </Button>

      {/* Animated background gradient */}
      <div className="absolute inset-0 -z-10 opacity-0 transition-opacity group-hover:opacity-100">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-transparent to-blue-500/10" />
      </div>
    </motion.div>
  );
};

const TaskResultCard = ({ task }: { task: TaskResult }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      layout
      className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-950"
    >
      <div
        className="cursor-pointer p-4"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn("rounded-lg p-2", getStatusColor(task.status))}>
              {task.status === "completed" && <CheckCircle className="h-4 w-4" />}
              {task.status === "failed" && <AlertCircle className="h-4 w-4" />}
              {task.status === "running" && <Loader2 className="h-4 w-4 animate-spin" />}
              {task.status === "pending" && <RefreshCw className="h-4 w-4" />}
            </div>
            <div>
              <p className="font-medium">{task.task}</p>
              <p className="text-sm text-gray-500">
                {task.agent} • {getRelativeTime(new Date(task.started_at))}
                {task.duration && ` • ${formatDuration(task.duration)}`}
              </p>
            </div>
          </div>
          <motion.div
            animate={{ rotate: expanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="h-5 w-5 text-gray-400" />
          </motion.div>
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-gray-200 dark:border-gray-800"
          >
            <div className="p-4">
              {task.result && (
                <div className="mb-4">
                  <p className="mb-2 text-sm font-medium text-gray-500">Result</p>
                  <pre className="overflow-auto rounded-lg bg-gray-50 p-3 text-xs dark:bg-gray-900">
                    {JSON.stringify(task.result, null, 2)}
                  </pre>
                </div>
              )}
              
              {task.error && (
                <div className="mb-4">
                  <p className="mb-2 text-sm font-medium text-red-500">Error</p>
                  <pre className="overflow-auto rounded-lg bg-red-50 p-3 text-xs text-red-600 dark:bg-red-950 dark:text-red-400">
                    {task.error}
                  </pre>
                </div>
              )}

              {task.logs.length > 0 && (
                <div>
                  <p className="mb-2 text-sm font-medium text-gray-500">Logs</p>
                  <div className="space-y-1">
                    {task.logs.map((log, i) => (
                      <div
                        key={i}
                        className={cn(
                          "rounded px-2 py-1 text-xs",
                          log.level === "error" && "bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400",
                          log.level === "warning" && "bg-yellow-50 text-yellow-600 dark:bg-yellow-950 dark:text-yellow-400",
                          log.level === "info" && "bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400",
                          log.level === "debug" && "bg-gray-50 text-gray-600 dark:bg-gray-900 dark:text-gray-400"
                        )}
                      >
                        <span className="font-mono">
                          [{new Date(log.timestamp).toISOString().slice(11, 19)}] {log.message}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// Main Component
export default function GodTierDashboard() {
  const queryClient = useQueryClient();
  const { socket, connected } = useWebSocket();
  const { data: metrics, isLoading: metricsLoading } = useSystemMetrics();
  const { data: agents, isLoading: agentsLoading } = useAgents();
  const [tasks, setTasks] = useState<TaskResult[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  // Advanced task execution with real-time updates
  const executeTask = useMutation({
    mutationFn: async ({ agent, task }: { agent: string; task: string }) => {
      const response = await fetch(`${API_URL}/api/agents/${agent}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task }),
      });
      if (!response.ok) throw new Error("Task execution failed");
      return response.json();
    },
    onSuccess: (data) => {
      toast.success("Task executed successfully");
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
    onError: (error) => {
      toast.error(`Execution failed: ${error.message}`);
    },
  });

  // WebSocket event listeners
  useEffect(() => {
    if (!socket) return;

    socket.on("task:update", (update: TaskResult) => {
      setTasks((prev) => {
        const index = prev.findIndex((t) => t.id === update.id);
        if (index >= 0) {
          const newTasks = [...prev];
          newTasks[index] = update;
          return newTasks;
        }
        return [update, ...prev].slice(0, 50); // Keep last 50 tasks
      });
    });

    socket.on("metrics:update", (newMetrics: SystemMetrics) => {
      queryClient.setQueryData(["systemMetrics"], newMetrics);
    });

    socket.on("agent:status", (agentUpdate: AgentStatus) => {
      queryClient.setQueryData(["agents"], (old: AgentStatus[] | undefined) => {
        if (!old) return [agentUpdate];
        const index = old.findIndex((a) => a.id === agentUpdate.id);
        if (index >= 0) {
          const newAgents = [...old];
          newAgents[index] = agentUpdate;
          return newAgents;
        }
        return old;
      });
    });

    return () => {
      socket.off("task:update");
      socket.off("metrics:update");
      socket.off("agent:status");
    };
  }, [socket, queryClient]);

  // Intelligent task suggestion
  const suggestTask = useCallback((agentName: string) => {
    const suggestions: Record<string, string[]> = {
      Claude: [
        "Analyze system performance and suggest optimizations",
        "Generate comprehensive security audit report",
        "Create intelligent workflow recommendations",
        "Predict system capacity requirements",
      ],
      Codex: [
        "Generate optimized API client with retry logic",
        "Create performance monitoring dashboard",
        "Build automated testing framework",
        "Implement real-time data pipeline",
      ],
    };
    return suggestions[agentName]?.[Math.floor(Math.random() * 4)] || "Custom task";
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey) {
        switch (e.key) {
          case "1":
            e.preventDefault();
            setSelectedAgent("claude");
            break;
          case "2":
            e.preventDefault();
            setSelectedAgent("codex");
            break;
          case "r":
            e.preventDefault();
            queryClient.invalidateQueries();
            toast.success("Data refreshed");
            break;
        }
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [queryClient]);

  // Calculate system health
  const systemHealth = metrics
    ? (() => {
        const cpu = metrics.cpu_percent;
        const memory = metrics.memory_percent;
        const errorRate = metrics.error_rate;
        
        if (cpu > 90 || memory > 90 || errorRate > 5) return "critical";
        if (cpu > 70 || memory > 70 || errorRate > 2) return "warning";
        return "healthy";
      })()
    : "unknown";

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
      {/* Animated background pattern */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 opacity-50" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-xl dark:border-gray-800 dark:bg-gray-950/80">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 text-white shadow-lg"
            >
              <Sparkles className="h-6 w-6" />
            </motion.div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                NSAI Orchestrator MCP
              </h1>
              <p className="text-xs text-gray-500">God-Tier Production Platform</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              <div className={cn(
                "h-2 w-2 rounded-full",
                connected ? "bg-green-500" : "bg-red-500"
              )} />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {connected ? "Real-time Connected" : "Offline"}
              </span>
            </div>

            {/* Quick Actions */}
            <Button variant="outline" size="sm">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* System Status Overview */}
        <div className="mb-8">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-2xl font-bold">System Overview</h2>
            <div className={cn(
              "rounded-full px-3 py-1 text-sm font-medium",
              systemHealth === "healthy" && "bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300",
              systemHealth === "warning" && "bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-300",
              systemHealth === "critical" && "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300",
              systemHealth === "unknown" && "bg-gray-100 text-gray-700 dark:bg-gray-900 dark:text-gray-300"
            )}>
              System {systemHealth}
            </div>
          </div>

          {metricsLoading ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-32 animate-pulse rounded-xl bg-gray-200 dark:bg-gray-800" />
              ))}
            </div>
          ) : metrics ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
              <MetricCard
                icon={Cpu}
                label="CPU Usage"
                value={metrics.cpu_percent.toFixed(1)}
                unit="%"
                trend={-2.3}
                status={metrics.cpu_percent > 90 ? "critical" : metrics.cpu_percent > 70 ? "warning" : "normal"}
              />
              <MetricCard
                icon={MemoryStick}
                label="Memory"
                value={formatBytes(metrics.memory_used)}
                unit={`/ ${formatBytes(metrics.memory_total)}`}
                status={metrics.memory_percent > 90 ? "critical" : metrics.memory_percent > 70 ? "warning" : "normal"}
              />
              <MetricCard
                icon={Network}
                label="Network I/O"
                value={formatBytes(metrics.network_in + metrics.network_out)}
                unit="/s"
                trend={5.7}
              />
              <MetricCard
                icon={Database}
                label="Cache Hit Rate"
                value={metrics.cache_hit_rate.toFixed(1)}
                unit="%"
                status={metrics.cache_hit_rate < 50 ? "warning" : "normal"}
              />
              <MetricCard
                icon={Zap}
                label="Requests/sec"
                value={metrics.requests_per_second.toFixed(0)}
                trend={12.4}
              />
              <MetricCard
                icon={Gauge}
                label="Avg Response"
                value={metrics.average_response_time.toFixed(0)}
                unit="ms"
                status={metrics.average_response_time > 1000 ? "warning" : "normal"}
              />
              <MetricCard
                icon={AlertCircle}
                label="Error Rate"
                value={metrics.error_rate.toFixed(2)}
                unit="%"
                status={metrics.error_rate > 5 ? "critical" : metrics.error_rate > 2 ? "warning" : "normal"}
              />
              <MetricCard
                icon={Globe}
                label="Active Connections"
                value={metrics.active_connections}
              />
            </div>
          ) : (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-600 dark:border-red-800 dark:bg-red-950 dark:text-red-400">
              Failed to load system metrics
            </div>
          )}
        </div>

        {/* Agents Section */}
        <div className="mb-8">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-2xl font-bold">Intelligent Agents</h2>
            <Button
              variant="outline"
              size="sm"
              onClick={() => queryClient.invalidateQueries({ queryKey: ["agents"] })}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>

          {agentsLoading ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-64 animate-pulse rounded-xl bg-gray-200 dark:bg-gray-800" />
              ))}
            </div>
          ) : agents && agents.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {agents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  onExecute={(agentId) => {
                    const task = suggestTask(agent.name);
                    executeTask.mutate({ agent: agentId, task });
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-gray-200 bg-gray-50 p-8 text-center text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400">
              No agents available
            </div>
          )}
        </div>

        {/* Task History */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-2xl font-bold">Task History</h2>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">
                {tasks.filter(t => t.status === "running").length} active
              </span>
              <span className="text-sm text-gray-500">•</span>
              <span className="text-sm text-gray-500">
                {tasks.length} total
              </span>
            </div>
          </div>

          {tasks.length > 0 ? (
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {tasks.map((task) => (
                  <TaskResultCard key={task.id} task={task} />
                ))}
              </AnimatePresence>
            </div>
          ) : (
            <div className="rounded-xl border border-gray-200 bg-gray-50 p-8 text-center text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400">
              No tasks executed yet. Select an agent to get started!
            </div>
          )}
        </div>
      </main>

      {/* Advanced Features Modal - would be implemented separately */}
      {/* Workflow Builder, Security Center, Analytics Dashboard, etc. */}
    </div>
  );
}

// Add missing import
const ChevronDown = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <polyline points="6 9 12 15 18 9"></polyline>
  </svg>
);