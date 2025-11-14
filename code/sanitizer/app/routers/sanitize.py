from fastapi import APIRouter
from app.models.request_models import PromptRequest
from app.services.sanitizer import sanitize

router = APIRouter()

@router.post("/sanitize")
def sanitize_prompt(req: PromptRequest):
    cleaned, status = sanitize(req.prompt)

    if status == "blocked":
        return {"status": "blocked", "reason": "Prompt injection detected"}

    return {"status": "ok", "clean_prompt": cleaned}
