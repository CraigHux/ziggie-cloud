# Flowise RAG Pipeline Setup Guide

> **Author**: Ziggie AI Pipeline Agent
> **Created**: 2025-12-27
> **Version**: 1.0.0

---

## Overview

This guide explains how to set up RAG (Retrieval-Augmented Generation) pipelines in Flowise for the Ziggie knowledge base. These pipelines enable natural language querying of:

1. **Knowledge Base** (185+ markdown files with game dev documentation)
2. **Codebase** (Python/TypeScript source code)

---

## Pipeline Files Created

| File | Purpose | Vector Store |
|------|---------|--------------|
| `knowledge-base-qa-pipeline.json` | Query knowledge base docs | In-Memory |
| `knowledge-base-qa-pinecone.json` | Query knowledge base docs | Pinecone (persistent) |
| `code-assistant-pipeline.json` | Query source code | In-Memory |

---

## Prerequisites

### 1. Flowise Running on VPS

```bash
# Flowise should be running on port 3001
# Access via: http://your-vps-ip:3001 or https://ziggie.your-domain.com/flowise

# Check Flowise status
docker ps | grep flowise
```

### 2. Ollama Models Required

```bash
# SSH to VPS and pull required models
docker exec -it ollama ollama pull llama3.2
docker exec -it ollama ollama pull nomic-embed-text
docker exec -it ollama ollama pull codellama:7b  # For code assistant
```

### 3. Data Mounted in Docker

Update `docker-compose.yml` to mount knowledge base:

```yaml
flowise:
  image: flowiseai/flowise:latest
  ports:
    - "3001:3000"
  volumes:
    # Mount knowledge base from host
    - /path/to/knowledge-base:/app/data/knowledge-base:ro
    # Mount codebase for code assistant
    - /path/to/ziggie-code:/app/data/ziggie-code:ro
  environment:
    - FLOWISE_USERNAME=admin
    - FLOWISE_PASSWORD=${FLOWISE_PASSWORD}
```

---

## Import Instructions

### Step 1: Access Flowise UI

1. Navigate to `http://your-vps:3001`
2. Login with credentials
3. Click "Chatflows" in the left sidebar

### Step 2: Import Pipeline

1. Click the **"+"** button to create new chatflow
2. In the top-right menu, click **"Load Chatflow"** or **"Import"**
3. Upload the JSON file (e.g., `knowledge-base-qa-pipeline.json`)
4. The nodes will appear on the canvas

### Step 3: Configure Ollama Connection

1. Click on the **Ollama Embeddings** node
2. Verify Base URL: `http://ollama:11434` (Docker network)
3. Click on the **Ollama Chat Model** node
4. Verify Base URL and Model Name

### Step 4: Configure Data Path

1. Click on the **Directory Loader** node
2. Update `Folder Path` to match your Docker mount:
   - Knowledge Base: `/app/data/knowledge-base`
   - Code Base: `/app/data/ziggie-code`

### Step 5: Save and Test

1. Click **"Save Chatflow"** in the top-right
2. Name your chatflow (e.g., "Ziggie Knowledge Base QA")
3. Click the **chat icon** to test
4. Ask a question: "What is the Elite AI agent team structure?"

---

## Pipeline Configurations

### Knowledge Base QA Pipeline

| Component | Configuration |
|-----------|---------------|
| **Document Loader** | DirectoryLoader with `.md,.txt` extensions |
| **Text Splitter** | MarkdownTextSplitter (1500 chars, 200 overlap) |
| **Embeddings** | Ollama nomic-embed-text |
| **Vector Store** | In-Memory (or Pinecone for persistence) |
| **Chat Model** | Ollama llama3.2 (temp: 0.3) |
| **Chain** | ConversationalRetrievalQA |
| **Memory** | BufferMemory for conversation history |

**Best for**: Documentation questions, best practices, architecture

### Code Assistant Pipeline

| Component | Configuration |
|-----------|---------------|
| **Document Loader** | DirectoryLoader with `.py,.ts,.tsx,.js` extensions |
| **Text Splitter** | CodeTextSplitter (2000 chars, 300 overlap) |
| **Embeddings** | Ollama nomic-embed-text |
| **Vector Store** | In-Memory |
| **Chat Model** | Ollama codellama:7b (temp: 0.1) |
| **Chain** | ConversationalRetrievalQA |
| **Memory** | BufferMemory |

**Best for**: Code explanations, implementation details, debugging

---

## Vector Store Recommendations

### Option 1: In-Memory (Default)

**Pros:**
- Zero setup required
- Fast for small-medium datasets
- No external dependencies

**Cons:**
- Data lost on restart
- Must re-index documents each time
- Memory usage scales with documents

**Best for**: Development, testing, small knowledge bases

### Option 2: Pinecone (Recommended for Production)

**Pros:**
- Persistent storage (survives restarts)
- Scales to millions of vectors
- Free tier: 1 index, 1M vectors
- Fast similarity search

**Cons:**
- Requires account setup
- External dependency
- Free tier limitations

**Setup:**
1. Create account at [pinecone.io](https://www.pinecone.io/)
2. Create index: `ziggie-knowledge-base`
3. Dimension: `768` (matches nomic-embed-text)
4. Metric: `cosine`
5. Add API key in Flowise credentials

### Option 3: ChromaDB (Alternative)

**Pros:**
- Open source, self-hosted
- Persistent local storage
- Good for medium datasets

**Cons:**
- Additional Docker container
- More setup complexity

---

## API Usage

### Get Chatflow ID

After saving, note the chatflow ID from the URL:
```
http://your-vps:3001/chatflows/abc123-def456-...
                              ^^^^^^^^^^^^^^^^
                              This is your chatflow ID
```

### Query via API

```bash
# Simple query
curl -X POST http://your-vps:3001/api/v1/prediction/YOUR_CHATFLOW_ID \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the Elite AI agents?"}'

# With session ID for conversation continuity
curl -X POST http://your-vps:3001/api/v1/prediction/YOUR_CHATFLOW_ID \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me more about HEPHAESTUS",
    "overrideConfig": {
      "sessionId": "user-session-123"
    }
  }'
```

### Python Integration

```python
import requests

FLOWISE_URL = "http://your-vps:3001"
CHATFLOW_ID = "your-chatflow-id"

def query_knowledge_base(question: str, session_id: str = None):
    """Query Ziggie knowledge base via Flowise RAG pipeline."""
    url = f"{FLOWISE_URL}/api/v1/prediction/{CHATFLOW_ID}"

    payload = {"question": question}
    if session_id:
        payload["overrideConfig"] = {"sessionId": session_id}

    response = requests.post(url, json=payload)
    return response.json()

# Usage
result = query_knowledge_base("What is the RTS game balance design?")
print(result["text"])
print("Sources:", result.get("sourceDocuments", []))
```

---

## Troubleshooting

### Issue: "Cannot connect to Ollama"

**Solution:**
```bash
# Check Ollama is running
docker ps | grep ollama

# Check Ollama network
docker network inspect ziggie-network

# Use correct URL in Flowise
# Docker network: http://ollama:11434
# External: http://your-vps:11434
```

### Issue: "No documents found"

**Solution:**
1. Check mount path in docker-compose.yml
2. Verify files exist: `docker exec flowise ls /app/data/knowledge-base`
3. Check file extensions match loader config

### Issue: "Embeddings timeout"

**Solution:**
```bash
# Pull embedding model if missing
docker exec ollama ollama pull nomic-embed-text

# Increase timeout in Flowise node config
# Or reduce chunk size to process fewer tokens
```

### Issue: "Memory usage high"

**Solution:**
- Reduce `topK` from 6 to 4
- Increase chunk size to reduce total chunks
- Switch to Pinecone for large datasets

---

## Performance Optimization

### For Knowledge Base (185 files)

| Setting | Recommended | Why |
|---------|-------------|-----|
| Chunk Size | 1500 | Balance context vs precision |
| Chunk Overlap | 200 | Maintain context across chunks |
| Top K | 6 | Sufficient for most queries |
| Temperature | 0.3 | More focused responses |

### For Codebase

| Setting | Recommended | Why |
|---------|-------------|-----|
| Chunk Size | 2000 | Functions/classes need more context |
| Chunk Overlap | 300 | Keep related code together |
| Top K | 8 | Code often spans multiple files |
| Temperature | 0.1 | Deterministic code answers |

---

## Maintenance

### Re-indexing Documents

When knowledge base is updated:
1. For in-memory: Restart Flowise container
2. For Pinecone: Delete index and re-upsert

```bash
# Restart Flowise to re-index
docker restart flowise
```

### Monitoring

```bash
# Check Flowise logs
docker logs flowise --tail 100

# Check API health
curl http://your-vps:3001/api/v1/health
```

---

## Next Steps

1. **Import pipelines** using instructions above
2. **Test with sample questions**
3. **Configure Pinecone** for production persistence
4. **Integrate with Ziggie Control Center** via API
5. **Add more specialized pipelines** (e.g., AWS docs, agent configs)

---

## Files Location

All pipeline files are stored at:
```
C:\Ziggie\flowise-pipelines\
├── knowledge-base-qa-pipeline.json     # Main KB pipeline (in-memory)
├── knowledge-base-qa-pinecone.json     # KB pipeline with Pinecone
├── code-assistant-pipeline.json        # Code query pipeline
└── FLOWISE-RAG-SETUP-GUIDE.md          # This guide
```

---

*Generated by Ziggie AI Pipeline Agent*
