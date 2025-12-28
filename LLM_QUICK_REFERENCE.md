# LLM INTEGRATION - QUICK REFERENCE CARD

## Access URLs

```
Frontend Test UI:  http://localhost:3001/llm-test
Backend API:       http://localhost:54112/api/llm
API Docs:          http://localhost:54112/docs
Ollama Direct:     http://localhost:11434
```

## Quick Commands

### Check Status
```bash
# All services
docker ps | grep ziggie

# LLM status
curl http://localhost:54112/api/llm/status

# List models
docker exec ziggie-ollama ollama list
```

### Model Management
```bash
# Pull new model
docker exec ziggie-ollama ollama pull mistral
docker exec ziggie-ollama ollama pull codellama:7b

# Remove model
docker exec ziggie-ollama ollama rm llama3.2
```

### Logs & Debugging
```bash
# Ollama logs
docker logs ziggie-ollama --tail 50 -f

# Backend logs
docker logs ziggie-backend --tail 50 -f

# Resource usage
docker stats ziggie-ollama ziggie-backend
```

### Service Control
```bash
# Restart services
docker-compose restart ollama backend

# Stop LLM service
docker-compose stop ollama

# Start LLM service
docker-compose start ollama
```

## API Examples

### Get Status (Public)
```bash
curl http://localhost:54112/api/llm/status
```

### Generate Text (Authenticated)
```bash
curl -X POST http://localhost:54112/api/llm/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2",
    "prompt": "Write a Python hello world",
    "stream": false,
    "temperature": 0.7
  }'
```

### List Models (Authenticated)
```bash
curl http://localhost:54112/api/llm/models \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Ollama not responding | `docker-compose restart ollama` |
| Backend errors | Check logs: `docker logs ziggie-backend` |
| Slow responses | Expected in CPU mode (11s+) |
| Model not found | Pull it: `docker exec ziggie-ollama ollama pull llama3.2` |
| Auth errors | Login at http://localhost:3001/login |

## Performance Expectations

| Metric | CPU Mode | GPU Mode (Future) |
|--------|----------|-------------------|
| First Request | ~11s | ~1s |
| Subsequent | ~5-8s | ~0.5s |
| Tokens/Second | 5-10 | 50-100 |

## Files Modified

```
C:\Ziggie\docker-compose.yml
C:\Ziggie\control-center\backend\api\llm.py (NEW)
C:\Ziggie\control-center\backend\main.py
C:\Ziggie\control-center\backend\requirements.txt
C:\Ziggie\control-center\frontend\src\App.jsx
C:\Ziggie\control-center\frontend\src\components\LLM\LLMTestPage.jsx (NEW)
```

## Key Metrics

- **Implementation Time:** 10 minutes
- **Models Available:** llama3.2 (2GB)
- **API Endpoints:** 4 (/status, /models, /generate, /chat)
- **Containers:** 4 running (mongodb, backend, frontend, ollama)
- **Status:** All healthy ✅

## Next Steps

1. Test UI at http://localhost:3001/llm-test
2. Pull additional models (mistral, codellama)
3. Week 1 Day 2: Implement streaming
4. Week 2: Add rate limiting & caching
5. Week 3: Production hardening

---
**Last Updated:** November 14, 2025
**Status:** Day 1 Complete ✅
