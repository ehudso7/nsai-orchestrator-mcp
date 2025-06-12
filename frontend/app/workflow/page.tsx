import dynamic from "next/dynamic";

// Dynamically import the god-tier workflow builder with no SSR
const WorkflowBuilder = dynamic(
  () => import("@/components/workflow-builder"),
  { 
    ssr: false,
    loading: () => (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-xl text-gray-300">Loading God-Tier Workflow Builder...</p>
        </div>
      </div>
    )
  }
);

export default function WorkflowPage() {
  return <WorkflowBuilder />;
}