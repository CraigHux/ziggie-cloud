import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get('http://ollama:11434/api/tags', timeout=5.0)
            print(f'Status: {response.status_code}')
            print(f'Response: {response.text[:200]}')
        except Exception as e:
            print(f'Error: {e}')

asyncio.run(test())
