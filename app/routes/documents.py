from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.dependencies.auth import get_current_user
from app.services.embedding_service import generate_embedding
from app.services.rag_service import extract_section
from app.dependencies.license_guard import check_license
from PyPDF2 import PdfReader
import os
import shutil
import uuid

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "data"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def normalize_act_name(raw_act: str):
    raw = raw_act.lower()

    if "income" in raw:
        return "Income Tax Act 1961"

    if "gst" in raw:
        return "GST Act 2017"

    if "companies" in raw:
        return "Companies Act 2013"

    return raw_act


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    act_name: str = Form(...),
    year: int = Form(...),
    db: Session = Depends(get_db),
    firm=Depends(check_license),
    current_user=Depends(get_current_user)
):

    try:
        # 1️⃣ Save file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2️⃣ Create document record
        document = Document(
            filename=file.filename,
            filepath=file_path,
            content_type=file.content_type,
            size=os.path.getsize(file_path),
            uploaded_by=current_user.id
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # 3️⃣ Extract text from PDF safely
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            raise HTTPException(status_code=400, detail="No readable text found in PDF.")

        # 4️⃣ Normalize Act Name once
        normalized_act = normalize_act_name(act_name)

        # 5️⃣ Basic chunking
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

        # 6️⃣ Create chunks with metadata
        for i, chunk_text in enumerate(chunks):

            embedding = generate_embedding(chunk_text)
            section_reference = extract_section(chunk_text)

            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
                embedding=embedding,
                act_name=normalized_act,
                section_reference=section_reference,
                year=year
            )

            db.add(chunk)

        db.commit()

        return {"message": "Document uploaded and processed successfully."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
