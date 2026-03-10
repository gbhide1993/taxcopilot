from sqlalchemy import text
from app.services.embedding_service import generate_embedding


# -------------------------------
# 1️⃣ Exact Section Lookup
# -------------------------------

def search_by_exact_section(db, act_name: str, section_reference: str):
    sql = """
        SELECT
            id AS chunk_id,
            document_id,
            chunk_index,
            content,
            section_reference,
            1.0 AS similarity
        FROM document_chunks
        WHERE act_name = :act_name
          AND section_reference = :section_reference
        ORDER BY chunk_index
    """

    result = db.execute(
        text(sql),
        {
            "act_name": act_name,
            "section_reference": section_reference
        }
    ).fetchall()

    return [
        {
            "chunk_id": r.chunk_id,
            "document_id": r.document_id,
            "chunk_index": r.chunk_index,
            "content": r.content,
            "section_reference": r.section_reference,
            "similarity": r.similarity
        }
        for r in result
    ]


# -------------------------------
# 2️⃣ Vector Semantic Search
# -------------------------------

def search_similar_chunks(db, question: str, act_name: str, top_k: int = 5):
    embedding = generate_embedding(question)

    sql = """
        SELECT
            id AS chunk_id,
            document_id,
            chunk_index,
            content,
            section_reference,
            1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
        FROM document_chunks
        WHERE act_name = :act_name
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :top_k
    """

    result = db.execute(
        text(sql),
        {
            "embedding": embedding,
            "act_name": act_name,
            "top_k": top_k
        }
    ).fetchall()

    return [
        {
            "chunk_id": r.chunk_id,
            "document_id": r.document_id,
            "chunk_index": r.chunk_index,
            "content": r.content,
            "section_reference": r.section_reference,
            "similarity": float(r.similarity)
        }
        for r in result
    ]
