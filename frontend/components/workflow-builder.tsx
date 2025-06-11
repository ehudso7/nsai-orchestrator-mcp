"use client";

import React, { useState, useCallback, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  Code,
  Sparkles,
  GitBranch,
  Zap,
  Plus,
  Play,
  Save,
  Download,
  Upload,
  Settings,
  Layers,
  Link,
  Unlink,
  Eye,
  EyeOff,
  Maximize2,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Loader2,
  Terminal,
  Database,
  Cloud,
  Shield,
  Workflow,
  Bot,
  FileCode,
  Network,
  Activity,
  Minus,
} from "lucide-react";
import { Button } from "./ui/button";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useHotkeys } from "react-hotkeys-hook";

// Node types for the workflow
type NodeType = "agent" | "condition" | "parallel" | "merge" | "transform" | "trigger" | "output";

interface WorkflowNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: {
    label: string;
    agent?: string;
    task?: string;
    config?: any;
  };
  inputs: string[];
  outputs: string[];
}

interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  condition?: string;
}

interface WorkflowState {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  executing: boolean;
  selectedNode: string | null;
  selectedEdge: string | null;
  zoom: number;
  offset: { x: number; y: number };
}

// AI-powered workflow suggestions
const useAISuggestions = (currentWorkflow: WorkflowState) => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyzeworkflow = useCallback(async () => {
    setIsAnalyzing(true);
    
    // Simulate AI analysis
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const newSuggestions = [
      "Add error handling after API calls",
      "Implement retry logic for failed operations",
      "Parallelize independent data processing",
      "Add caching layer before expensive operations",
      "Implement circuit breaker for external services",
    ];
    
    setSuggestions(newSuggestions.slice(0, 3));
    setIsAnalyzing(false);
  }, []);

  return { suggestions, isAnalyzing, analyzeworkflow };
};

// Visual Programming Canvas
const WorkflowCanvas = ({ workflow, onUpdate }: { workflow: WorkflowState; onUpdate: (workflow: WorkflowState) => void }) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedNode, setDraggedNode] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStart, setConnectionStart] = useState<string | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Handle node dragging
  const handleNodeMouseDown = (nodeId: string, e: React.MouseEvent) => {
    e.preventDefault();
    setDraggedNode(nodeId);
    setIsDragging(true);
  };

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = (e.clientX - rect.left - workflow.offset.x) / workflow.zoom;
    const y = (e.clientY - rect.top - workflow.offset.y) / workflow.zoom;
    
    setMousePosition({ x, y });

    if (isDragging && draggedNode) {
      const updatedNodes = workflow.nodes.map(node =>
        node.id === draggedNode ? { ...node, position: { x, y } } : node
      );
      onUpdate({ ...workflow, nodes: updatedNodes });
    }
  }, [isDragging, draggedNode, workflow, onUpdate]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    setDraggedNode(null);
    if (isConnecting) {
      setIsConnecting(false);
      setConnectionStart(null);
    }
  }, [isConnecting]);

  // Handle connection creation
  const handleOutputClick = (nodeId: string) => {
    if (!isConnecting) {
      setIsConnecting(true);
      setConnectionStart(nodeId);
    } else if (connectionStart && connectionStart !== nodeId) {
      // Create new edge
      const newEdge: WorkflowEdge = {
        id: `edge-${Date.now()}`,
        source: connectionStart,
        target: nodeId,
      };
      onUpdate({
        ...workflow,
        edges: [...workflow.edges, newEdge],
      });
      setIsConnecting(false);
      setConnectionStart(null);
    }
  };

  // Render node based on type
  const renderNode = (node: WorkflowNode) => {
    const isSelected = workflow.selectedNode === node.id;
    
    const nodeIcons = {
      agent: Brain,
      condition: GitBranch,
      parallel: Layers,
      merge: Link,
      transform: RefreshCw,
      trigger: Zap,
      output: Download,
    };
    
    const Icon = nodeIcons[node.type] || Brain;
    
    return (
      <motion.div
        key={node.id}
        className={cn(
          "absolute w-48 rounded-lg border-2 bg-card p-4 shadow-lg cursor-move transition-all",
          isSelected && "border-primary ring-2 ring-primary/20",
          !isSelected && "border-border hover:border-primary/50"
        )}
        style={{
          left: node.position.x,
          top: node.position.y,
          transform: `scale(${workflow.zoom})`,
          transformOrigin: "top left",
        }}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: workflow.zoom, opacity: 1 }}
        onMouseDown={(e) => handleNodeMouseDown(node.id, e)}
        onClick={() => onUpdate({ ...workflow, selectedNode: node.id })}
        whileHover={{ scale: workflow.zoom * 1.02 }}
        whileTap={{ scale: workflow.zoom * 0.98 }}
      >
        <div className="flex items-center gap-2 mb-2">
          <div className={cn(
            "p-2 rounded-md",
            node.type === "agent" && "bg-purple-500/20 text-purple-500",
            node.type === "condition" && "bg-blue-500/20 text-blue-500",
            node.type === "parallel" && "bg-green-500/20 text-green-500",
            node.type === "transform" && "bg-yellow-500/20 text-yellow-500",
            node.type === "trigger" && "bg-red-500/20 text-red-500",
            node.type === "output" && "bg-gray-500/20 text-gray-500"
          )}>
            <Icon className="h-4 w-4" />
          </div>
          <span className="font-medium text-sm">{node.data.label}</span>
        </div>
        
        {node.data.agent && (
          <div className="text-xs text-muted-foreground mb-1">
            Agent: {node.data.agent}
          </div>
        )}
        
        {/* Input/Output ports */}
        <div className="absolute -left-2 top-1/2 -translate-y-1/2">
          <div className="w-4 h-4 rounded-full bg-primary border-2 border-background" />
        </div>
        <div
          className="absolute -right-2 top-1/2 -translate-y-1/2 cursor-pointer"
          onClick={(e) => {
            e.stopPropagation();
            handleOutputClick(node.id);
          }}
        >
          <div className="w-4 h-4 rounded-full bg-primary border-2 border-background hover:scale-125 transition-transform" />
        </div>
      </motion.div>
    );
  };

  // Render edge connections
  const renderEdge = (edge: WorkflowEdge) => {
    const sourceNode = workflow.nodes.find(n => n.id === edge.source);
    const targetNode = workflow.nodes.find(n => n.id === edge.target);
    
    if (!sourceNode || !targetNode) return null;
    
    const x1 = sourceNode.position.x + 192; // Width of node
    const y1 = sourceNode.position.y + 40; // Half height
    const x2 = targetNode.position.x;
    const y2 = targetNode.position.y + 40;
    
    // Calculate control points for smooth curve
    const dx = x2 - x1;
    const dy = y2 - y1;
    const cx1 = x1 + dx * 0.5;
    const cy1 = y1;
    const cx2 = x2 - dx * 0.5;
    const cy2 = y2;
    
    const isSelected = workflow.selectedEdge === edge.id;
    
    return (
      <g key={edge.id}>
        <path
          d={`M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`}
          fill="none"
          stroke={isSelected ? "hsl(var(--primary))" : "hsl(var(--muted-foreground))"}
          strokeWidth={isSelected ? 3 : 2}
          strokeDasharray={edge.condition ? "5,5" : "0"}
          className="transition-all cursor-pointer hover:stroke-primary"
          onClick={() => onUpdate({ ...workflow, selectedEdge: edge.id })}
        />
        {edge.label && (
          <text
            x={(x1 + x2) / 2}
            y={(y1 + y2) / 2}
            textAnchor="middle"
            className="fill-foreground text-xs"
          >
            {edge.label}
          </text>
        )}
      </g>
    );
  };

  // Render connection preview while dragging
  const renderConnectionPreview = () => {
    if (!isConnecting || !connectionStart) return null;
    
    const sourceNode = workflow.nodes.find(n => n.id === connectionStart);
    if (!sourceNode) return null;
    
    const x1 = sourceNode.position.x + 192;
    const y1 = sourceNode.position.y + 40;
    const x2 = mousePosition.x;
    const y2 = mousePosition.y;
    
    return (
      <path
        d={`M ${x1} ${y1} L ${x2} ${y2}`}
        fill="none"
        stroke="hsl(var(--primary))"
        strokeWidth={2}
        strokeDasharray="5,5"
        className="pointer-events-none animate-pulse"
      />
    );
  };

  return (
    <div
      ref={canvasRef}
      className="relative w-full h-full overflow-hidden bg-background"
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* Grid background */}
      <div
        className="absolute inset-0 bg-grid opacity-10"
        style={{
          backgroundPosition: `${workflow.offset.x}px ${workflow.offset.y}px`,
          backgroundSize: `${50 * workflow.zoom}px ${50 * workflow.zoom}px`,
        }}
      />
      
      {/* Edges */}
      <svg className="absolute inset-0 pointer-events-none">
        <g
          style={{
            transform: `translate(${workflow.offset.x}px, ${workflow.offset.y}px) scale(${workflow.zoom})`,
          }}
        >
          {workflow.edges.map(renderEdge)}
          {renderConnectionPreview()}
        </g>
      </svg>
      
      {/* Nodes */}
      <div
        className="absolute inset-0"
        style={{
          transform: `translate(${workflow.offset.x}px, ${workflow.offset.y}px)`,
        }}
      >
        {workflow.nodes.map(renderNode)}
      </div>
    </div>
  );
};

// Node palette for drag-and-drop
const NodePalette = ({ onAddNode }: { onAddNode: (type: NodeType) => void }) => {
  const nodeTypes: { type: NodeType; icon: any; label: string; description: string }[] = [
    { type: "agent", icon: Brain, label: "AI Agent", description: "Claude or Codex agent" },
    { type: "condition", icon: GitBranch, label: "Condition", description: "Conditional branching" },
    { type: "parallel", icon: Layers, label: "Parallel", description: "Execute in parallel" },
    { type: "merge", icon: Link, label: "Merge", description: "Merge parallel branches" },
    { type: "transform", icon: RefreshCw, label: "Transform", description: "Data transformation" },
    { type: "trigger", icon: Zap, label: "Trigger", description: "Workflow trigger" },
    { type: "output", icon: Download, label: "Output", description: "Save results" },
  ];

  return (
    <div className="w-64 h-full border-r border-border bg-card/50 p-4">
      <h3 className="font-semibold mb-4">Workflow Nodes</h3>
      <div className="space-y-2">
        {nodeTypes.map(({ type, icon: Icon, label, description }) => (
          <motion.div
            key={type}
            className="p-3 rounded-lg border border-border bg-background cursor-pointer hover:border-primary/50 transition-all"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onAddNode(type)}
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-md bg-primary/10 text-primary">
                <Icon className="h-4 w-4" />
              </div>
              <div>
                <div className="font-medium text-sm">{label}</div>
                <div className="text-xs text-muted-foreground">{description}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      <div className="mt-6 p-3 rounded-lg bg-primary/10 border border-primary/20">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <span className="font-medium text-sm">AI Assistant</span>
        </div>
        <p className="text-xs text-muted-foreground">
          Drag nodes to canvas and connect them to build your workflow. AI will suggest optimizations.
        </p>
      </div>
    </div>
  );
};

// Main Workflow Builder Component
export default function WorkflowBuilder() {
  const [workflow, setWorkflow] = useState<WorkflowState>({
    nodes: [],
    edges: [],
    executing: false,
    selectedNode: null,
    selectedEdge: null,
    zoom: 1,
    offset: { x: 0, y: 0 },
  });

  const [showGrid, setShowGrid] = useState(true);
  const [showMinimap, setShowMinimap] = useState(true);
  const { suggestions, isAnalyzing, analyzeworkflow } = useAISuggestions(workflow);

  // Keyboard shortcuts
  useHotkeys("delete", () => {
    if (workflow.selectedNode) {
      setWorkflow(prev => ({
        ...prev,
        nodes: prev.nodes.filter(n => n.id !== prev.selectedNode),
        edges: prev.edges.filter(e => e.source !== prev.selectedNode && e.target !== prev.selectedNode),
        selectedNode: null,
      }));
    }
  });

  useHotkeys("cmd+s", (e) => {
    e.preventDefault();
    handleSave();
  });

  useHotkeys("cmd+z", () => {
    // Implement undo
    toast.info("Undo not implemented yet");
  });

  useHotkeys("cmd+shift+z", () => {
    // Implement redo
    toast.info("Redo not implemented yet");
  });

  const handleAddNode = (type: NodeType) => {
    const newNode: WorkflowNode = {
      id: `node-${Date.now()}`,
      type,
      position: { x: 200 + Math.random() * 200, y: 200 + Math.random() * 200 },
      data: {
        label: type.charAt(0).toUpperCase() + type.slice(1),
      },
      inputs: type === "trigger" ? [] : ["input"],
      outputs: type === "output" ? [] : ["output"],
    };

    setWorkflow(prev => ({
      ...prev,
      nodes: [...prev.nodes, newNode],
    }));

    toast.success(`Added ${type} node`);
  };

  const handleExecute = async () => {
    setWorkflow(prev => ({ ...prev, executing: true }));
    
    // Simulate workflow execution
    const executionSteps = workflow.nodes.length;
    for (let i = 0; i < executionSteps; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success(`Executed step ${i + 1}/${executionSteps}`);
    }
    
    setWorkflow(prev => ({ ...prev, executing: false }));
    toast.success("Workflow execution completed!");
  };

  const handleSave = () => {
    const workflowData = JSON.stringify(workflow, null, 2);
    const blob = new Blob([workflowData], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `workflow-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Workflow saved!");
  };

  const handleLoad = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);
        setWorkflow(data);
        toast.success("Workflow loaded!");
      } catch (error) {
        toast.error("Failed to load workflow");
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Toolbar */}
      <div className="h-16 border-b border-border flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Workflow className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">AI Workflow Builder</h2>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => document.getElementById("file-input")?.click()}
            >
              <Upload className="h-4 w-4 mr-2" />
              Load
            </Button>
            <input
              id="file-input"
              type="file"
              accept=".json"
              className="hidden"
              onChange={handleLoad}
            />
            
            <Button size="sm" variant="outline" onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setShowGrid(!showGrid)}
          >
            {showGrid ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
          </Button>
          
          <Button
            size="sm"
            variant="outline"
            onClick={() => setWorkflow(prev => ({ ...prev, zoom: Math.min(prev.zoom + 0.1, 2) }))}
          >
            <Plus className="h-4 w-4" />
          </Button>
          
          <span className="text-sm text-muted-foreground">
            {Math.round(workflow.zoom * 100)}%
          </span>
          
          <Button
            size="sm"
            variant="outline"
            onClick={() => setWorkflow(prev => ({ ...prev, zoom: Math.max(prev.zoom - 0.1, 0.5) }))}
          >
            <Minus className="h-4 w-4" />
          </Button>
          
          <Button
            size="sm"
            variant={workflow.executing ? "destructive" : "default"}
            onClick={handleExecute}
            disabled={workflow.nodes.length === 0}
          >
            {workflow.executing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Executing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Execute
              </>
            )}
          </Button>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        <NodePalette onAddNode={handleAddNode} />
        
        <div className="flex-1 relative">
          <WorkflowCanvas workflow={workflow} onUpdate={setWorkflow} />
          
          {/* AI Suggestions */}
          <AnimatePresence>
            {suggestions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="absolute top-4 right-4 w-80 p-4 rounded-lg bg-card border border-border shadow-lg"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-primary" />
                    <span className="font-medium text-sm">AI Suggestions</span>
                  </div>
                  <button
                    onClick={() => analyzeworkflow()}
                    className="text-xs text-muted-foreground hover:text-foreground"
                  >
                    {isAnalyzing ? <Loader2 className="h-3 w-3 animate-spin" /> : <RefreshCw className="h-3 w-3" />}
                  </button>
                </div>
                
                <div className="space-y-2">
                  {suggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      className="p-2 rounded-md bg-primary/10 text-sm cursor-pointer hover:bg-primary/20 transition-colors"
                      onClick={() => toast.info("Apply suggestion: " + suggestion)}
                    >
                      {suggestion}
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* Properties panel */}
          {workflow.selectedNode && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="absolute top-4 left-4 w-80 p-4 rounded-lg bg-card border border-border shadow-lg"
            >
              <h3 className="font-medium mb-3">Node Properties</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm text-muted-foreground">Label</label>
                  <input
                    type="text"
                    className="w-full mt-1 px-3 py-2 rounded-md bg-background border border-input"
                    value={workflow.nodes.find(n => n.id === workflow.selectedNode)?.data.label || ""}
                    onChange={(e) => {
                      setWorkflow(prev => ({
                        ...prev,
                        nodes: prev.nodes.map(n =>
                          n.id === prev.selectedNode
                            ? { ...n, data: { ...n.data, label: e.target.value } }
                            : n
                        ),
                      }));
                    }}
                  />
                </div>
                
                {workflow.nodes.find(n => n.id === workflow.selectedNode)?.type === "agent" && (
                  <div>
                    <label className="text-sm text-muted-foreground">Agent</label>
                    <select className="w-full mt-1 px-3 py-2 rounded-md bg-background border border-input">
                      <option value="claude">Claude</option>
                      <option value="codex">Codex</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}