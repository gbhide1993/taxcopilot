from app.models.ai_query_log import AIQueryLog
from datetime import datetime


def log_ai_query(db, user_id, question, answer, references):

    safe_answer = answer if answer else "REJECTED: No answer generated due to safety checks."

    summary = safe_answer[:500]

    log = AIQueryLog(
        user_id=user_id,
        question=question,
        answer_summary=summary,
        references=references
    )

    db.add(log)
    db.commit()
