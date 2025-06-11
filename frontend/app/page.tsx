"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [status, setStatus] = useState("Loading...");
  const [response, setResponse] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => res.json())
      .then((data) => setStatus(data.status || "Connected"))
      .catch(() => setStatus("Backend unreachable"));
  }, []);

  const handleCodex = async () => {
    try {
      setError("");
      const r = await fetch(`${API_URL}/api/agents/codex/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: "Generate API client code" }),
      });
      const d = await r.json();
      setResponse(d.result || JSON.stringify(d, null, 2));
    } catch (e) {
      setError("Failed to contact Codex agent");
    }
  };

  const handleClaude = async () => {
    try {
      setError("");
      const r = await fetch(`${API_URL}/api/agents/claude/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: "Summarize system status" }),
      });
      const d = await r.json();
      setResponse(d.result || JSON.stringify(d, null, 2));
    } catch (e) {
      setError("Failed to contact Claude agent");
    }
  };

  return (
    <main className="container mx-auto p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          NSAI Orchestrator MCP
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Production-grade multi-agent orchestration platform
        </p>
        
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="flex items-center space-x-2">
            <div
              className={`w-3 h-3 rounded-full ${
                status === "Backend unreachable" ? "bg-red-500" : "bg-green-500"
              }`}
            ></div>
            <span className="text-gray-700">{status}</span>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Agent Controls</h2>
          <div className="space-x-4">
            <button
              onClick={handleCodex}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Execute Codex Agent
            </button>
            <button
              onClick={handleClaude}
              className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
            >
              Analyze with Claude
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="text-red-800 font-medium">Error</div>
            <div className="text-red-600">{error}</div>
          </div>
        )}

        {response && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Agent Response</h2>
            <div className="bg-gray-50 border rounded-lg p-4 overflow-auto">
              <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                {response}
              </pre>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
