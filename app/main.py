from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.routes import auth
from app.models import user, client, notice, document, document_chunk
from app.routes import clients, notices, documents, search, rag, system, users, sections, drafts, risk, dashboard, appeals, settings
from app.dependencies.license_guard import check_license


load_dotenv()

app = FastAPI(title="Private Tax Notice Copilot")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)






app.include_router(auth.router)

app.include_router(search.router)

app.include_router(system.router)

app.include_router(users.router)

app.include_router(clients.router, dependencies=[Depends(check_license)])

app.include_router(notices.router, dependencies=[Depends(check_license)])

app.include_router(documents.router, dependencies=[Depends(check_license)])

app.include_router(rag.router, dependencies=[Depends(check_license)])

app.include_router(sections.router)

app.include_router(drafts.router)

app.include_router(risk.router)

app.include_router(dashboard.router)

app.include_router(appeals.router)

app.include_router(settings.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"db_status": "connected", "result": result.scalar()}
    

@app.on_event("startup")
def on_startup():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    


@app.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {
        "message": "Access granted",
        "user": current_user.email
        
    }

