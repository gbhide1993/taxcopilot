from app.services.search_service import (
    search_similar_chunks,
    search_by_exact_section
)
from app.services.llm_service import generate_answer
import re


MAX_CONTEXT_CHARS = 3000
MIN_SIMILARITY = 0.65
MIN_CHUNKS_REQUIRED = 1


# -------------------------------
# Section Detection
# -------------------------------

def extract_section(query: str):
    match = re.search(r"section\s+(\d+[A-Za-z]*)", query, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def detect_act(query: str):
    if "gst" in query.lower():
        return "GST Act 2017"
    if "companies act" in query.lower():
        return "Companies Act 2013"

    return "Income Tax Act 1961"


# -------------------------------
# RAG ENGINE
# -------------------------------

def generate_rag_answer(db, question: str):

    act_name = detect_act(question)
    requested_section = extract_section(question)

    # 1️⃣ EXACT SECTION OVERRIDE
    if requested_section:
        exact_chunks = search_by_exact_section(
            db,
            act_name,
            requested_section
        )

        if exact_chunks:
            chunks = exact_chunks
        else:
            return {
                "answer": None,
                "references": [],
                "reason": "Section not found in provided documents."
            }

    else:
        # 2️⃣ Semantic fallback
        chunks = search_similar_chunks(
            db,
            question,
            act_name,
            top_k=5
        )

    # -------------------------------
    # SAFETY CHECKS
    # -------------------------------

    if not chunks or len(chunks) < MIN_CHUNKS_REQUIRED:
        return {
            "answer": None,
            "references": [],
            "reason": "Insufficient relevant sources."
        }

    if not requested_section:
        valid_chunks = [
            c for c in chunks
            if c["similarity"] >= MIN_SIMILARITY
        ]

        if not valid_chunks:
            return {
                "answer": None,
                "references": [],
                "reason": "Low similarity match."
            }

        chunks = valid_chunks

    # -------------------------------
    # Build context
    # -------------------------------

    context_parts = []
    total_chars = 0

    for c in chunks:
        if total_chars + len(c["content"]) > MAX_CONTEXT_CHARS:
            break
        context_parts.append(c["content"])
        total_chars += len(c["content"])

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a Chartered Accountant AI assistant.

STRICT RULES:
- Answer ONLY from the provided CONTEXT.
- Do NOT use external knowledge.
- If context does not clearly contain the answer, say:
  "Section not found in provided documents."

CONTEXT:
{context}

QUESTION:
{question}

Answer clearly and precisely:
"""

    answer = generate_answer(prompt)

    if not answer:
        return {
            "answer": None,
            "references": [],
            "reason": "No answer generated."
        }

    return {
        "answer": answer.strip(),
        "references": [
            {
                "chunk_id": c["chunk_id"],
                "document_id": c["document_id"],
                "chunk_index": c["chunk_index"],
                "similarity": c["similarity"],
                "section_reference": c["section_reference"],
                "excerpt": c["content"][:250]
            }
            for c in chunks
        ]
    }
