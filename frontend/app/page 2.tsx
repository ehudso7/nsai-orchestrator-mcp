"use client"
import { useEffect, useState } from "react"

export default function Home() {
  const [status, setStatus] = useState("Loading...")
  const [response, setResponse] = useState("")

  useEffect(() => {
    fetch("http://localhost:4141/")
      .then(res => res.json())
      .then(data => setStatus(data.status))
  }, [])

  const handleCodex = async () => {
    const r = await fetch("http://localhost:4141/mcp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ method: "execute", params: { agent: "codex", task: "generate API client" } })
    })
    const d = await r.json()
    setResponse(d.result)
  }

  const handleClaude = async () => {
    const r = await fetch("http://localhost:4141/mcp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ method: "analyze", params: { agent: "claude", task: "summarize memory graph" } })
    })
    const d = await r.json()
    setResponse(d.result)
  }

  return (
    <main className="p-10">
      <h1 className="text-3xl font-bold">MCP Orchestrator</h1>
      <p className="text-gray-500">{status}</p>
      <div className="mt-6 flex gap-4">
        <button onClick={handleCodex} className="px-4 py-2 bg-blue-600 text-white">Run Codex</button>
        <button onClick={handleClaude} className="px-4 py-2 bg-purple-600 text-white">Run Claude</button>
      </div>
      <div className="mt-6 bg-gray-100 p-4 border rounded">
        <pre>{response}</pre>
      </div>
    </main>
  )
}
