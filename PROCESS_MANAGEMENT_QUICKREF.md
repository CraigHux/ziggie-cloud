# Process Management Quick Reference

## File Location
`C:\Ziggie\coordinator\agent_spawner.py`

---

## Method Summary

### Core Methods

| Method | Purpose | Key Features |
|--------|---------|--------------|
| `spawn_agent(request)` | Spawn new agent process | PID tracking, verification, error handling |
| `get_agent_status(agent_id)` | Get comprehensive health info | CPU, memory, status, exit codes |
| `cleanup(agent_id, force)` | Terminate processes | 3-stage graceful shutdown, zombie reaping |

### Utility Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `monitor_all_agents()` | Get status for all agents | Dict[agent_id, status] |
| `reap_zombies()` | Clean up zombie processes | List[agent_id] |
| `get_process_summary()` | Aggregate statistics | Stats dict |
| `check_process_health(agent_id)` | Quick health check | bool |
| `kill_agent(agent_id, force)` | Kill specific agent | bool |

---

## Common Usage Patterns

### Spawn an Agent
```python
response = spawner.spawn_agent(request)
if response.status == AgentStatus.RUNNING:
    print(f"Success! PID: {response.pid}")
```

### Check Health
```python
# Quick check
is_healthy = spawner.check_process_health("L2.1.1")

# Detailed status
status = spawner.get_agent_status("L2.1.1")
print(f"CPU: {status['cpu_percent']}%")
print(f"Memory: {status['memory_mb']} MB")
print(f"Health: {status['health']}")
```

### Graceful Shutdown
```python
# Single agent
spawner.cleanup(agent_id="L2.1.1")

# All agents
spawner.cleanup()

# Force kill
spawner.cleanup(force=True)
```

### Monitor All
```python
summary = spawner.get_process_summary()
print(f"Running: {summary['running']}")
print(f"Failed: {summary['failed']}")
print(f"Total Memory: {summary['total_memory_mb']} MB")
```

### Handle Zombies
```python
reaped = spawner.reap_zombies()
for agent_id in reaped:
    print(f"Reaped zombie: {agent_id}")
```

---

## Status Response Structure

```python
{
    "agent_id": "L2.1.1",
    "process_alive": True,
    "process_status": "running",
    "exit_code": None,
    "is_zombie": False,
    "cpu_percent": 5.2,
    "memory_mb": 45.3,
    "runtime_seconds": 120,
    "num_threads": 4,
    "cmdline": "python -c ...",
    "health": "healthy",  # healthy/zombie/completed/failed/unknown
    "persistent_status": "running",
    "started_at": "2025-11-09T10:30:00",
    "progress": 50
}
```

---

## Health States

| State | Meaning |
|-------|---------|
| `healthy` | Process alive and running normally |
| `zombie` | Process terminated but not reaped |
| `completed` | Exited successfully (code 0) |
| `failed` | Exited with error (code != 0) |
| `unknown` | Cannot determine status |

---

## Cleanup Stages

1. **SIGTERM** (10s wait) - Graceful shutdown
2. **SIGTERM** (5s wait) - Second chance
3. **SIGKILL** (5s wait) - Force termination

Use `force=True` to skip directly to SIGKILL.

---

## Error Handling

| Exception | Meaning | Action |
|-----------|---------|--------|
| `subprocess.SubprocessError` | Spawn failed | Cleanup, mark failed |
| `psutil.Error` | Process monitoring failed | Log, return limited info |
| `OSError` | File/OS error | Cleanup, mark failed |
| `psutil.NoSuchProcess` | Process disappeared | Clean up tracking |

---

## State Manager Integration

- **On spawn**: Status → SPAWNING → RUNNING
- **On complete**: Status → COMPLETED (exit code 0)
- **On failure**: Status → FAILED (exit code != 0)
- **On cleanup**: Status → CANCELLED

---

## Process Verification

After spawning:
1. Check `process.poll()` - should be None
2. Wait 100ms for startup
3. Verify with `psutil.Process(pid).is_running()`
4. Store in `self.processes` dict

---

## Resource Monitoring

- **CPU**: `proc.cpu_percent(interval=0.1)` - 100ms sample
- **Memory**: `proc.memory_info().rss / (1024*1024)` - MB
- **Runtime**: `time.time() - proc.create_time()` - seconds
- **Threads**: `proc.num_threads()` - count

---

## Best Practices

1. **Always verify after spawn** - Don't trust that spawn succeeded
2. **Use graceful cleanup** - Give processes time to clean up
3. **Monitor periodically** - Not continuously (expensive)
4. **Reap zombies regularly** - Prevent accumulation
5. **Update state always** - Keep persistence current
6. **Handle missing processes** - They might disappear
7. **Log everything** - Debug issues easier

---

## Testing

Run comprehensive tests:
```bash
cd C:\Ziggie
python test_process_management.py
```

Tests cover:
- Spawn and monitoring
- Health checks
- Graceful cleanup
- Multiple agents
- Zombie handling
- Error cases

---

## Troubleshooting Quick Guide

**Process won't die?**
→ Try `cleanup(force=True)`

**Status not updating?**
→ Check state file permissions, disk space

**High resource usage?**
→ Check `get_process_summary()`, look for leaks

**Zombies accumulating?**
→ Run `reap_zombies()` periodically

**Spawn fails immediately?**
→ Check logs in agent_dir/stderr.log

---

## Dependencies

- `psutil >= 5.9.0` (required)
- Python 3.7+ (required)

---

## Key Features

✓ PID tracking and verification
✓ Real-time health monitoring
✓ Zombie process handling
✓ Graceful 3-stage shutdown
✓ Child process cleanup
✓ Comprehensive error handling
✓ State persistence
✓ Cross-platform support

---

## Performance

- Health check: ~10-20ms per agent
- Graceful cleanup: 15-20s per agent
- Force cleanup: <1s per agent
- Zombie reaping: ~5ms per zombie

---

For detailed documentation, see:
`C:\Ziggie\PROCESS_MANAGEMENT_DOCUMENTATION.md`
