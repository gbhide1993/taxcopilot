from pydantic import BaseModel, EmailStr
from typing import Optional


class ClientCreate(BaseModel):
    name: str
    pan: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class ClientResponse(BaseModel):
    id: int
    name: str
    pan: str
    email: Optional[str]
    phone: Optional[str]

    class Config:
        orm_mode = True
