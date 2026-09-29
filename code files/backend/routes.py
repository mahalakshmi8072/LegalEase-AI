from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from backend.ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
_generator = GeminiDocumentGenerator()

class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=3, max_length=120)
    parties: str = Field(..., min_length=3, max_length=5000)
    terms: str = Field(..., min_length=3, max_length=10000)
    effective_date: str = Field(..., min_length=2, max_length=100)

    @field_validator("document_type", "parties", "terms", "effective_date")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value

class GenerateResponse(BaseModel):
    document_text: str
    document_type: str
    effective_date: str

@router.post("/generate", response_model=GenerateResponse, tags=["documents"])
def generate_document(payload: DocumentRequest):
    try:
        text = _generator.generate_document(
            document_type=payload.document_type,
            parties=payload.parties,
            terms=payload.terms,
            effective_date=payload.effective_date,
        )
        return GenerateResponse(
            document_text=text,
            document_type=payload.document_type,
            effective_date=payload.effective_date,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {exc}") from exc
