from pydantic import BaseModel, EmailStr
from typing import Optional, List


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "user"


class LoginIn(BaseModel):
    email: EmailStr
    password: str

class ForgetPassword(BaseModel):
    email: EmailStr
       
class ResetPassword(BaseModel):
    email: EmailStr
    otp_code: int
    new_password: str

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
    total_units: int   
    remaining_units: Optional[int] = None
    

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category: CategoryOut
    
    stock_status: Optional[str] = None



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


class OrderDetailsOut(BaseModel):
    order_id: int
    cart_id: int
    total_amount: float
    order_status: str
    order_time: str
    products: list[dict]



class CartItemIn(BaseModel):
    product_id: int
    quantity: int = 1


class CartCreate(BaseModel):
    user_id: int
    products: List[CartItemIn]  


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
