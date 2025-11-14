import httpx

SANITIZER_URL = "http://sanitizer:8000/sanitize"

async def sanitize_prompt(prompt: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(SANITIZER_URL, json={"prompt": prompt})
        return r.json()
