from sqlalchemy.orm import Session
from app.models.client import Client
from sqlalchemy import or_
from app.services.audit_service import log_action
from app import models



def create_client(db: Session, client_data, user_id: int):
    new_client = Client(
        name=client_data.name,
        pan=client_data.pan,
        email=client_data.email,
        phone=client_data.phone,
        created_by=user_id,
        assigned_to=user_id  # optional: auto-assign creator
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    # 🔥 Audit Log
    log_action(
        db=db,
        user_id=user_id,
        role_name=new_client.owner.role.name if new_client.owner else "UNKNOWN",
        action="CREATE_CLIENT",
        entity_type="Client",
        entity_id=new_client.id,
        details={"client_name": new_client.name}
    )

    return new_client



def get_clients(db, current_user):
    print("USER ROLE OBJECT:", current_user.role)
    print("ROLE NAME:", current_user.role.name)
    role_name = current_user.role.name

    # ADMIN & SENIOR_CA can see all clients
    if role_name in ["ADMIN", "SENIOR_CA"]:
        return db.query(models.Client).all()

    # Other roles can only see assigned clients
    return (
        db.query(models.Client)
        .filter(models.Client.assigned_to == current_user.id)
        .all()
    )


def update_client(db: Session, client_id: int, client_data, user_id: int):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        return None

    client.name = client_data.name
    client.pan = client_data.pan
    client.email = client_data.email
    client.phone = client_data.phone

    db.commit()
    db.refresh(client)

    # 🔥 Audit Log
    log_action(
        db=db,
        user_id=user_id,
        role_name=client.owner.role.name if client.owner else "UNKNOWN",
        action="UPDATE_CLIENT",
        entity_type="Client",
        entity_id=client.id,
        details={"updated_name": client.name}
    )

    return client

