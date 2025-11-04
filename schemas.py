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



class OrderCreate(BaseModel):
    user_id: int
    cart_id: int


class OrderOut(BaseModel):
    id: int
    user_id: int
    cart_id: int
    order_status: str
    order_time: str
    total_amount: float
    user_email: Optional[str] = None



class CartCreate(BaseModel):
    user_id: int
    product_ids: list[int]


class CartOut(BaseModel):
    id: int
    user_id: int
    created_at: str
    products: list[dict]



class CheckoutOut(BaseModel):
    order_id: int
    user_id: int
    cart_id: int
    total_amount: float
    order_status: str
    order_time: str
