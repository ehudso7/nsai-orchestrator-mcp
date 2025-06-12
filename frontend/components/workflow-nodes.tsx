import React from "react";
import { 
  GitBranch, 
  RefreshCw, 
  AlertTriangle, 
  Timer, 
  Variable,
  Calculator,
  Filter,
  Shuffle,
  ListChecks,
  ArrowRightLeft,
  Database,
  FileJson,
  Hash,
  Braces
} from "lucide-react";

export interface AdvancedNode {
  type: string;
  icon: React.ComponentType<any>;
  label: string;
  description: string;
  category: string;
  defaultData: any;
  inputs: string[];
  outputs: string[];
  configFields: ConfigField[];
}

export interface ConfigField {
  name: string;
  label: string;
  type: "text" | "number" | "select" | "boolean" | "code" | "json";
  defaultValue?: any;
  options?: { value: string; label: string }[];
  placeholder?: string;
  required?: boolean;
  validation?: (value: any) => string | null;
}

export const advancedNodeTypes: Record<string, AdvancedNode> = {
  // Control Flow Nodes
  condition: {
    type: "condition",
    icon: GitBranch,
    label: "Conditional",
    description: "Branch execution based on conditions",
    category: "Control Flow",
    defaultData: {
      condition: "",
      operator: "equals",
      value: "",
      combineLogic: "and"
    },
    inputs: ["input"],
    outputs: ["true", "false"],
    configFields: [
      {
        name: "condition",
        label: "Condition Expression",
        type: "code",
        placeholder: "e.g., {{input.status}} === 'success'",
        required: true
      },
      {
        name: "operator",
        label: "Operator",
        type: "select",
        defaultValue: "equals",
        options: [
          { value: "equals", label: "Equals (==)" },
          { value: "not_equals", label: "Not Equals (!=)" },
          { value: "greater", label: "Greater Than (>)" },
          { value: "less", label: "Less Than (<)" },
          { value: "contains", label: "Contains" },
          { value: "regex", label: "Regex Match" },
          { value: "custom", label: "Custom Expression" }
        ]
      }
    ]
  },

  loop: {
    type: "loop",
    icon: RefreshCw,
    label: "Loop",
    description: "Iterate over arrays or repeat N times",
    category: "Control Flow",
    defaultData: {
      loopType: "forEach",
      items: "{{input.items}}",
      maxIterations: 100,
      parallelExecution: false
    },
    inputs: ["input"],
    outputs: ["item", "completed"],
    configFields: [
      {
        name: "loopType",
        label: "Loop Type",
        type: "select",
        defaultValue: "forEach",
        options: [
          { value: "forEach", label: "For Each Item" },
          { value: "while", label: "While Condition" },
          { value: "times", label: "Repeat N Times" },
          { value: "map", label: "Map Transform" },
          { value: "filter", label: "Filter Items" },
          { value: "reduce", label: "Reduce/Aggregate" }
        ]
      },
      {
        name: "items",
        label: "Items to Process",
        type: "code",
        placeholder: "{{input.items}} or ['item1', 'item2']"
      },
      {
        name: "maxIterations",
        label: "Max Iterations",
        type: "number",
        defaultValue: 100,
        validation: (value) => value > 0 ? null : "Must be positive"
      },
      {
        name: "parallelExecution",
        label: "Execute in Parallel",
        type: "boolean",
        defaultValue: false
      }
    ]
  },

  errorHandler: {
    type: "errorHandler",
    icon: AlertTriangle,
    label: "Error Handler",
    description: "Catch and handle errors gracefully",
    category: "Control Flow",
    defaultData: {
      errorTypes: ["all"],
      retryCount: 3,
      retryDelay: 1000,
      fallbackValue: null
    },
    inputs: ["input"],
    outputs: ["success", "error", "fallback"],
    configFields: [
      {
        name: "errorTypes",
        label: "Error Types to Catch",
        type: "select",
        defaultValue: ["all"],
        options: [
          { value: "all", label: "All Errors" },
          { value: "timeout", label: "Timeout Errors" },
          { value: "api", label: "API Errors" },
          { value: "validation", label: "Validation Errors" },
          { value: "custom", label: "Custom Pattern" }
        ]
      },
      {
        name: "retryCount",
        label: "Retry Count",
        type: "number",
        defaultValue: 3
      },
      {
        name: "retryDelay",
        label: "Retry Delay (ms)",
        type: "number",
        defaultValue: 1000
      },
      {
        name: "fallbackValue",
        label: "Fallback Value",
        type: "json",
        placeholder: "Default value on error"
      }
    ]
  },

  delay: {
    type: "delay",
    icon: Timer,
    label: "Delay",
    description: "Add delay or wait for conditions",
    category: "Control Flow",
    defaultData: {
      delayType: "fixed",
      duration: 1000,
      waitCondition: ""
    },
    inputs: ["input"],
    outputs: ["output"],
    configFields: [
      {
        name: "delayType",
        label: "Delay Type",
        type: "select",
        defaultValue: "fixed",
        options: [
          { value: "fixed", label: "Fixed Duration" },
          { value: "random", label: "Random Duration" },
          { value: "exponential", label: "Exponential Backoff" },
          { value: "condition", label: "Wait for Condition" }
        ]
      },
      {
        name: "duration",
        label: "Duration (ms)",
        type: "number",
        defaultValue: 1000
      }
    ]
  },

  // Data Processing Nodes
  transform: {
    type: "transform",
    icon: ArrowRightLeft,
    label: "Transform",
    description: "Transform data using expressions",
    category: "Data Processing",
    defaultData: {
      transformType: "map",
      expression: "{{input}}",
      outputFormat: "same"
    },
    inputs: ["input"],
    outputs: ["output"],
    configFields: [
      {
        name: "transformType",
        label: "Transform Type",
        type: "select",
        defaultValue: "map",
        options: [
          { value: "map", label: "Map/Transform" },
          { value: "filter", label: "Filter" },
          { value: "reduce", label: "Reduce/Aggregate" },
          { value: "sort", label: "Sort" },
          { value: "group", label: "Group By" },
          { value: "flatten", label: "Flatten" },
          { value: "merge", label: "Merge Objects" }
        ]
      },
      {
        name: "expression",
        label: "Transform Expression",
        type: "code",
        placeholder: "e.g., {{input.map(item => item.value)}}"
      }
    ]
  },

  variable: {
    type: "variable",
    icon: Variable,
    label: "Variable",
    description: "Store and retrieve variables",
    category: "Data Processing",
    defaultData: {
      operation: "set",
      variableName: "myVar",
      value: "",
      scope: "workflow"
    },
    inputs: ["input"],
    outputs: ["output"],
    configFields: [
      {
        name: "operation",
        label: "Operation",
        type: "select",
        defaultValue: "set",
        options: [
          { value: "set", label: "Set Variable" },
          { value: "get", label: "Get Variable" },
          { value: "increment", label: "Increment" },
          { value: "append", label: "Append to Array" },
          { value: "delete", label: "Delete Variable" }
        ]
      },
      {
        name: "variableName",
        label: "Variable Name",
        type: "text",
        required: true
      },
      {
        name: "value",
        label: "Value",
        type: "code",
        placeholder: "{{input}} or static value"
      }
    ]
  },

  calculator: {
    type: "calculator",
    icon: Calculator,
    label: "Calculator",
    description: "Perform mathematical operations",
    category: "Data Processing",
    defaultData: {
      operation: "add",
      values: [],
      expression: ""
    },
    inputs: ["input"],
    outputs: ["result"],
    configFields: [
      {
        name: "operation",
        label: "Operation",
        type: "select",
        defaultValue: "add",
        options: [
          { value: "add", label: "Addition" },
          { value: "subtract", label: "Subtraction" },
          { value: "multiply", label: "Multiplication" },
          { value: "divide", label: "Division" },
          { value: "average", label: "Average" },
          { value: "sum", label: "Sum Array" },
          { value: "min", label: "Minimum" },
          { value: "max", label: "Maximum" },
          { value: "custom", label: "Custom Expression" }
        ]
      },
      {
        name: "expression",
        label: "Math Expression",
        type: "code",
        placeholder: "e.g., {{input.a}} + {{input.b}} * 2"
      }
    ]
  },

  filter: {
    type: "filter",
    icon: Filter,
    label: "Filter",
    description: "Filter arrays based on conditions",
    category: "Data Processing",
    defaultData: {
      filterExpression: "",
      filterType: "include",
      caseSensitive: true
    },
    inputs: ["input"],
    outputs: ["filtered", "rejected"],
    configFields: [
      {
        name: "filterExpression",
        label: "Filter Expression",
        type: "code",
        placeholder: "e.g., item.status === 'active'",
        required: true
      },
      {
        name: "filterType",
        label: "Filter Type",
        type: "select",
        defaultValue: "include",
        options: [
          { value: "include", label: "Include Matching" },
          { value: "exclude", label: "Exclude Matching" },
          { value: "split", label: "Split Into Two Arrays" }
        ]
      }
    ]
  },

  // Integration Nodes
  database: {
    type: "database",
    icon: Database,
    label: "Database",
    description: "Query or update database",
    category: "Integration",
    defaultData: {
      operation: "query",
      connectionString: "",
      query: "",
      parameters: {}
    },
    inputs: ["input"],
    outputs: ["result", "error"],
    configFields: [
      {
        name: "operation",
        label: "Operation",
        type: "select",
        defaultValue: "query",
        options: [
          { value: "query", label: "Query (SELECT)" },
          { value: "insert", label: "Insert" },
          { value: "update", label: "Update" },
          { value: "delete", label: "Delete" },
          { value: "transaction", label: "Transaction" }
        ]
      },
      {
        name: "query",
        label: "SQL Query",
        type: "code",
        placeholder: "SELECT * FROM users WHERE id = :id",
        required: true
      }
    ]
  },

  jsonParser: {
    type: "jsonParser",
    icon: FileJson,
    label: "JSON Parser",
    description: "Parse or stringify JSON data",
    category: "Data Processing",
    defaultData: {
      operation: "parse",
      pretty: true,
      errorHandling: "default"
    },
    inputs: ["input"],
    outputs: ["output", "error"],
    configFields: [
      {
        name: "operation",
        label: "Operation",
        type: "select",
        defaultValue: "parse",
        options: [
          { value: "parse", label: "Parse JSON String" },
          { value: "stringify", label: "Convert to JSON" },
          { value: "validate", label: "Validate JSON" },
          { value: "transform", label: "Transform Structure" }
        ]
      },
      {
        name: "pretty",
        label: "Pretty Print",
        type: "boolean",
        defaultValue: true
      }
    ]
  },

  aggregator: {
    type: "aggregator",
    icon: ListChecks,
    label: "Aggregator",
    description: "Aggregate multiple inputs",
    category: "Data Processing",
    defaultData: {
      waitForAll: true,
      timeout: 30000,
      aggregationType: "array"
    },
    inputs: ["input1", "input2", "input3"],
    outputs: ["aggregated"],
    configFields: [
      {
        name: "waitForAll",
        label: "Wait for All Inputs",
        type: "boolean",
        defaultValue: true
      },
      {
        name: "aggregationType",
        label: "Aggregation Type",
        type: "select",
        defaultValue: "array",
        options: [
          { value: "array", label: "Array" },
          { value: "object", label: "Object" },
          { value: "concat", label: "Concatenate" },
          { value: "merge", label: "Deep Merge" }
        ]
      }
    ]
  },

  randomizer: {
    type: "randomizer",
    icon: Shuffle,
    label: "Randomizer",
    description: "Generate random values or shuffle",
    category: "Data Processing",
    defaultData: {
      randomType: "number",
      min: 0,
      max: 100,
      seed: null
    },
    inputs: ["input"],
    outputs: ["output"],
    configFields: [
      {
        name: "randomType",
        label: "Random Type",
        type: "select",
        defaultValue: "number",
        options: [
          { value: "number", label: "Random Number" },
          { value: "boolean", label: "Random Boolean" },
          { value: "uuid", label: "Generate UUID" },
          { value: "sample", label: "Random Sample" },
          { value: "shuffle", label: "Shuffle Array" }
        ]
      },
      {
        name: "min",
        label: "Minimum",
        type: "number",
        defaultValue: 0
      },
      {
        name: "max",
        label: "Maximum",
        type: "number",
        defaultValue: 100
      }
    ]
  },

  validator: {
    type: "validator",
    icon: ListChecks,
    label: "Validator",
    description: "Validate data against schema",
    category: "Data Processing",
    defaultData: {
      validationType: "schema",
      schema: {},
      customRules: []
    },
    inputs: ["input"],
    outputs: ["valid", "invalid", "errors"],
    configFields: [
      {
        name: "validationType",
        label: "Validation Type",
        type: "select",
        defaultValue: "schema",
        options: [
          { value: "schema", label: "JSON Schema" },
          { value: "regex", label: "Regex Pattern" },
          { value: "custom", label: "Custom Rules" },
          { value: "type", label: "Type Check" }
        ]
      },
      {
        name: "schema",
        label: "Validation Schema",
        type: "json",
        placeholder: "JSON Schema or validation rules"
      }
    ]
  }
};

// Helper function to create node from type
export function createNode(type: string, position: { x: number; y: number }) {
  const nodeType = advancedNodeTypes[type];
  if (!nodeType) return null;

  return {
    id: `${type}-${Date.now()}`,
    type: nodeType.type,
    position,
    data: {
      label: nodeType.label,
      ...nodeType.defaultData,
      _nodeType: type
    }
  };
}