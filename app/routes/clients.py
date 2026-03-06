from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.client_schema import ClientCreate, ClientResponse
from app.services.client_service import create_client, get_clients, update_client
from app.dependencies.auth import get_current_user
from app.dependencies.role_guard import require_role
from app.models.client import Client
from app.services.compliance_service import get_client_compliance_summary
from app.services.client_service import get_client_notice_history

router = APIRouter(prefix="/clients", tags=["Clients"])



@router.post("/", response_model=ClientResponse)
def create_new_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "SENIOR_CA"]))
):
    return create_client(db, client, current_user.id)


@router.get("/", response_model=list[ClientResponse])
def list_clients(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_clients(db, current_user)


@router.put("/{client_id}", response_model=ClientResponse)
def update_existing_client(
    client_id: int,
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "SENIOR_CA"]))
):
    existing_client = db.query(Client).filter(Client.id == client_id).first()

    if not existing_client:
        raise HTTPException(status_code=404, detail="Client not found")

    # If not ADMIN, allow update only if assigned_to matches
    if current_user.role.name != "ADMIN":
        if existing_client.assigned_to != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to update this client"
            )

    updated = update_client(db, client_id, client, current_user.id)

    return updated


@router.get("/{client_id}/compliance-summary")
def compliance_summary(
    client_id: int,
    db: Session = Depends(get_db)
):
    return get_client_compliance_summary(db, client_id)

@router.get("/{client_id}")
def get_client_detail(
    client_id: int,
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return client


@router.get("/")
def list_clients(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_clients(db)


@router.get("/{client_id}/notices")
def client_notices(
    client_id: int,
    db: Session = Depends(get_db)
):

    return get_client_notice_history(db, client_id)