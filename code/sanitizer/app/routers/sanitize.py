from fastapi import APIRouter
from app.models.request_models import PromptRequest
from app.services.sanitizer import sanitize

router = APIRouter()

@router.post("/sanitize")
def sanitize_prompt(req: PromptRequest):
    """
    Limpa e normaliza o prompt (remove caracteres invisíveis, unicode, etc).
    Não faz validação de segurança - isso é responsabilidade do GuardRail.
    """
    cleaned, status = sanitize(req.prompt)
    return {"status": "ok", "clean_prompt": cleaned}
