async def call_llm(prompt: str):
    return {
        "model": "fake-llm",
        "response": f"Resposta gerada para: {prompt}"
    }
