from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role_id: int


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role_id: int
    is_active: bool

    class Config:
        from_attributes = True
