from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services.search_service import search_similar_chunks
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/search", tags=["Search"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/")
def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    results = search_similar_chunks(
        db,
        request.query,
        request.top_k
    )

    return {
        "query": request.query,
        "results": [
            {
                "chunk_id": r["chunk_id"],
                "document_id": r["document_id"],
                "chunk_index": r["chunk_index"],
                "similarity": r["similarity"],
                "content": r["content"]
            }
            for r in results
        ]
    }
