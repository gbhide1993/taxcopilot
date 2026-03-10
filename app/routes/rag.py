from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.services.rag_service import generate_rag_answer
from app.models.ai_query_log import AIQueryLog
from app.services.ai_log_service import log_ai_query
from app.dependencies.license_guard import check_license


router = APIRouter(prefix="/rag", tags=["RAG"])


class RAGRequest(BaseModel):
    question: str


@router.post("/")
def ask_question(
    request: RAGRequest,
    db: Session = Depends(get_db),
    firm=Depends(check_license),
    current_user=Depends(get_current_user)
):
    response = generate_rag_answer(db, request.question)

    # ✅ Log AI query
    log_ai_query(
        db=db,
        user_id=current_user.id,
        question=request.question,
        answer=response["answer"],
        references=response["references"]
    )

    return {
        "question": request.question,
        "answer": response["answer"],
        "references": response["references"]
    }
