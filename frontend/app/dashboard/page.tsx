"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Line, Bar } from "react-chartjs-2";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [agentActivity, setAgentActivity] = useState<any[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [agentStats, setAgentStats] = useState<Record<string, number>>({});
  const router = useRouter();

  useEffect(() => {
    // Check authentication
    checkAuth();
    
    // Fetch initial metrics
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);

    // WebSocket connection
    const ws = apiClient.createWebSocket();
    if (ws) {
      ws.onopen = () => {
        setWsConnected(true);
        console.log("WebSocket connected");
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "agent_response" || data.type === "agent_result") {
          setAgentActivity(prev => [...prev.slice(-19), {
            ...data,
            timestamp: new Date().toISOString()
          }]);
          
          // Update agent stats
          if (data.agent) {
            setAgentStats(prev => ({
              ...prev,
              [data.agent]: (prev[data.agent] || 0) + 1
            }));
          }
        } else if (data.type === "workflow_update") {
          setAgentActivity(prev => [...prev.slice(-19), {
            agent: "workflow",
            status: data.message,
            timestamp: new Date().toISOString()
          }]);
        }
      };

      ws.onclose = () => {
        setWsConnected(false);
        console.log("WebSocket disconnected");
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        toast.error("WebSocket connection failed");
      };
    }

    return () => {
      clearInterval(interval);
      ws?.close();
    };
  }, [router]);

  const checkAuth = async () => {
    try {
      await apiClient.getCurrentUser();
    } catch (error) {
      router.push('/login');
    }
  };

  const fetchMetrics = async () => {
    try {
      const data = await apiClient.getMetrics();
      setMetrics(data);
    } catch (error) {
      console.error("Failed to fetch metrics:", error);
    }
  };

  const chartData = {
    labels: agentActivity.slice(-10).map((_, i) => `T-${9 - i}`),
    datasets: [
      {
        label: "Agent Activity",
        data: agentActivity.slice(-10).map((_, i) => {
          const recentActivity = agentActivity.slice(0, i + 1);
          return recentActivity.filter(a => 
            new Date(a.timestamp).getTime() > Date.now() - 60000
          ).length;
        }),
        borderColor: "rgb(75, 192, 192)",
        backgroundColor: "rgba(75, 192, 192, 0.5)",
        tension: 0.4,
      },
    ],
  };

  const agentStatusData = {
    labels: ["Claude", "Codex", "Orchestrator", "Memory"],
    datasets: [
      {
        label: "Agent Calls",
        data: [
          agentStats.claude || 0,
          agentStats.codex || 0,
          agentStats.orchestrator || 0,
          agentStats.memory || 0
        ],
        backgroundColor: [
          "rgba(147, 51, 234, 0.5)",
          "rgba(59, 130, 246, 0.5)",
          "rgba(34, 197, 94, 0.5)",
          "rgba(251, 146, 60, 0.5)",
        ],
        borderColor: [
          "rgba(147, 51, 234, 1)",
          "rgba(59, 130, 246, 1)",
          "rgba(34, 197, 94, 1)",
          "rgba(251, 146, 60, 1)",
        ],
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-5xl font-bold mb-8 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
          NSAI Orchestrator Dashboard
        </h1>

        {/* Status Bar */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-gray-400 text-sm font-medium">System Status</h3>
            <p className="text-3xl font-bold text-green-400">Healthy</p>
            <p className="text-gray-500 text-sm">All systems operational</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-gray-400 text-sm font-medium">Active Connections</h3>
            <p className="text-3xl font-bold">{metrics?.connections || 0}</p>
            <p className="text-gray-500 text-sm">WebSocket: {wsConnected ? "Connected" : "Disconnected"}</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-gray-400 text-sm font-medium">Cache Keys</h3>
            <p className="text-3xl font-bold">{metrics?.cache_keys || 0}</p>
            <p className="text-gray-500 text-sm">Redis storage</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-gray-400 text-sm font-medium">Total API Calls</h3>
            <p className="text-3xl font-bold">{Object.values(agentStats).reduce((a, b) => a + b, 0)}</p>
            <p className="text-gray-500 text-sm">Across all agents</p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">Agent Activity</h2>
            <Line data={chartData} options={{ responsive: true, maintainAspectRatio: false }} height={300} />
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">Agent Status</h2>
            <Bar data={agentStatusData} options={{ responsive: true, maintainAspectRatio: false }} height={300} />
          </div>
        </div>

        {/* Activity Feed */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold mb-4">Real-time Activity</h2>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {agentActivity.length === 0 ? (
              <p className="text-gray-500">No activity yet. Execute agents to see real-time updates.</p>
            ) : (
              agentActivity.slice().reverse().map((activity, index) => (
                <div key={index} className="flex items-center space-x-4 text-sm p-2 rounded hover:bg-gray-700/50 transition-colors">
                  <span className="text-gray-500 min-w-[80px]">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </span>
                  <span className={`font-medium min-w-[100px] ${
                    activity.agent === "claude" ? "text-purple-400" : 
                    activity.agent === "codex" ? "text-blue-400" : 
                    activity.agent === "orchestrator" ? "text-green-400" :
                    activity.agent === "memory" ? "text-orange-400" :
                    activity.agent === "workflow" ? "text-yellow-400" :
                    "text-gray-400"
                  }`}>
                    {activity.agent?.toUpperCase() || "SYSTEM"}
                  </span>
                  <span className="text-gray-300 flex-1">
                    {activity.status || activity.data?.status || "Processing..."}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}