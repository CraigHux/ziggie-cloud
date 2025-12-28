const http = require("http");

const OLLAMA_URL = process.env.OLLAMA_URL || "http://ollama:11434";
const N8N_URL = process.env.N8N_URL || "http://n8n:5678";

// MCP Server Registry
const mcpServers = {
  ollama: { url: OLLAMA_URL, description: "Local LLM via Ollama" },
  n8n: { url: N8N_URL, description: "Workflow automation" },
};

// MCP Tool Registry
const mcpTools = {
  chat: {
    name: "chat",
    description: "Send a message to an LLM and get a response",
    inputSchema: {
      type: "object",
      properties: {
        message: { type: "string", description: "The message to send" },
        model: { type: "string", description: "Model to use", default: "mistral:7b" }
      },
      required: ["message"]
    }
  },
  list_models: {
    name: "list_models",
    description: "List available LLM models",
    inputSchema: { type: "object", properties: {} }
  },
  trigger_workflow: {
    name: "trigger_workflow",
    description: "Trigger an n8n workflow",
    inputSchema: {
      type: "object",
      properties: {
        workflow_id: { type: "string", description: "ID of the workflow to trigger" },
        data: { type: "object", description: "Data to pass to workflow" }
      },
      required: ["workflow_id"]
    }
  }
};

// JSON-RPC handler
async function handleJsonRpc(body) {
  const request = JSON.parse(body);
  const { method, params, id } = request;
  
  try {
    let result;
    
    switch (method) {
      case "initialize":
        result = {
          protocolVersion: "2024-11-05",
          capabilities: { tools: {} },
          serverInfo: { name: "ziggie-mcp-gateway", version: "1.0.0" }
        };
        break;
        
      case "tools/list":
        result = { tools: Object.values(mcpTools) };
        break;
        
      case "tools/call":
        const { name, arguments: args } = params;
        result = await executeTool(name, args);
        break;
        
      case "resources/list":
        result = { resources: [] };
        break;
        
      case "prompts/list":
        result = { prompts: [] };
        break;
        
      default:
        return { jsonrpc: "2.0", error: { code: -32601, message: "Method not found" }, id };
    }
    
    return { jsonrpc: "2.0", result, id };
  } catch (error) {
    return { jsonrpc: "2.0", error: { code: -32000, message: error.message }, id };
  }
}

// Tool execution
async function executeTool(name, args) {
  switch (name) {
    case "chat":
      return await callOllama(args.message, args.model || "mistral:7b");
    case "list_models":
      return await listModels();
    case "trigger_workflow":
      return await triggerWorkflow(args.workflow_id, args.data || {});
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// Ollama integration
async function callOllama(message, model) {
  const response = await fetch(`${OLLAMA_URL}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model, prompt: message, stream: false })
  });
  const data = await response.json();
  return { content: [{ type: "text", text: data.response }] };
}

async function listModels() {
  const response = await fetch(`${OLLAMA_URL}/api/tags`);
  const data = await response.json();
  return { content: [{ type: "text", text: JSON.stringify(data.models) }] };
}

// n8n integration
async function triggerWorkflow(workflowId, data) {
  // Placeholder - needs n8n API key configuration
  return { content: [{ type: "text", text: `Workflow ${workflowId} triggered` }] };
}

// HTTP Server
const server = http.createServer(async (req, res) => {
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  
  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }
  
  const url = new URL(req.url, `http://${req.headers.host}`);
  
  // Health check
  if (url.pathname === "/health") {
    res.end(JSON.stringify({ status: "ok", service: "mcp-gateway", version: "1.0.0" }));
    return;
  }
  
  // Service info
  if (url.pathname === "/" && req.method === "GET") {
    res.end(JSON.stringify({
      service: "Ziggie MCP Gateway",
      version: "1.0.0",
      protocol: "MCP 2024-11-05",
      servers: Object.keys(mcpServers),
      tools: Object.keys(mcpTools),
      endpoints: {
        mcp: "/mcp (POST - JSON-RPC)",
        health: "/health",
        servers: "/servers",
        tools: "/tools"
      }
    }));
    return;
  }
  
  // List servers
  if (url.pathname === "/servers" && req.method === "GET") {
    res.end(JSON.stringify({ servers: mcpServers }));
    return;
  }
  
  // List tools
  if (url.pathname === "/tools" && req.method === "GET") {
    res.end(JSON.stringify({ tools: mcpTools }));
    return;
  }
  
  // MCP JSON-RPC endpoint (both /mcp and / for nginx proxying)
  if ((url.pathname === "/mcp" || url.pathname === "/") && req.method === "POST") {
    let body = "";
    req.on("data", chunk => body += chunk);
    req.on("end", async () => {
      try {
        const response = await handleJsonRpc(body);
        res.end(JSON.stringify(response));
      } catch (error) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: error.message }));
      }
    });
    return;
  }
  
  // 404
  res.writeHead(404);
  res.end(JSON.stringify({ error: "Not found" }));
});

server.listen(8080, () => console.log("MCP Gateway running on port 8080"));
