from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from guardrails.hub import BiasCheck
from guardrails import Guard

app = FastAPI(title="Bias GuardRail Microservice")

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def root():
    return {"message": "Bias GuardRail running", "status": "healthy"}

@app.post("/validate")
async def validate(data: PromptRequest):
    try:
        output = validate_prompt(data.prompt)
        return {
            "valid": True,
            "prompt": output
        }

    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={"valid": False, "error": str(e)}
        )

def validate_prompt(prompt: str):
    guard = Guard().use(
        BiasCheck(threshold=0.9, on_fail="exception")
    )

    validated = guard.validate(prompt)
    return validated.validated_output



