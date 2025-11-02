from pydantic import BaseModel, EmailStr
from typing import Optional, List


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str]


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = 0.0
    category_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None

class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category: CategoryOut
