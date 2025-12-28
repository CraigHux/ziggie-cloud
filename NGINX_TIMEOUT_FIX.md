# Nginx Timeout Fix for Sim Studio Chat Endpoint

## Problem

Chat endpoint returns 504 Gateway Timeout after 60 seconds because Ollama LLM responses take longer than nginx's default timeout.

## Solution

Add extended timeout configuration to the `/sim/` location block in nginx.conf.

## File to Edit

**Location**: `c:\Ziggie\ziggie-cloud-repo\nginx\nginx.conf`

**Lines to modify**: 102-106

## Current Configuration (BROKEN)

```nginx
# Sim Studio
location /sim/ {
    proxy_pass http://sim_studio/;
    proxy_set_header Host $host;
}
```

## Fixed Configuration

```nginx
# Sim Studio
location /sim/ {
    proxy_pass http://sim_studio/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Extended timeouts for LLM chat endpoints
    proxy_read_timeout 180s;      # Allow 3 minutes for LLM response
    proxy_connect_timeout 180s;   # Allow 3 minutes to connect to backend
    proxy_send_timeout 180s;      # Allow 3 minutes to send request
}
```

## Deployment Steps

1. Edit the file:
   ```bash
   cd c:/Ziggie/ziggie-cloud-repo
   # Edit nginx/nginx.conf with the fix above
   ```

2. Validate nginx configuration:
   ```bash
   docker exec ziggie-nginx nginx -t
   ```

3. Reload nginx (without downtime):
   ```bash
   docker exec ziggie-nginx nginx -s reload
   ```

   OR restart the container:
   ```bash
   docker restart ziggie-nginx
   ```

4. Test the fix:
   ```bash
   python c:/Ziggie/test_chat_direct.py
   ```

   Should see:
   - Status code: 200 (not 504)
   - Agent response in JSON
   - Turn count incremented
   - Status changed to "running"

## Expected Result

After applying this fix:
- ✅ Chat endpoint will work correctly
- ✅ LLM responses will be returned to client
- ✅ Turn counting will work
- ✅ Status transitions will work
- ✅ Full simulation workflow will pass

## Why 180 seconds?

- First LLM request (model loading): 30-90 seconds
- Subsequent requests: 10-30 seconds
- 180s (3 minutes) provides comfortable buffer
- Backend already has 120s timeout (see temp_sim_studio.py line 139)
- Gateway timeout should be >= backend timeout

## Alternative: Async/Streaming Response (Future Enhancement)

For production, consider:
1. **WebSocket-based chat** - Stream tokens as they're generated
2. **Polling pattern** - Return 202 Accepted, poll for completion
3. **Faster LLM model** - Use `llama3.2:3b` instead of `mistral:7b` for lower latency

But for now, extending the timeout is the quickest fix.
