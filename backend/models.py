from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str   #hash


class UserRegister(SQLModel):
    username: str
    password: str


class UserLogin(SQLModel):
    username: str
    password: str

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    user_id: int


class CategoryCreate(SQLModel):
    name: str


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str = Field(max_length=11)
    email: str
    city: str
    user_id: int
    category_id: Optional[int] = None


class ContactCreate(SQLModel):
    name: str
    phone: str = Field(..., regex=r'^\d{11}$')
    email: EmailStr
    city: str
    category_id: Optional[int] = None


class ContactUpdate(SQLModel):
    name: Optional[str] 
    phone: Optional[str] = Field(None, regex=r'^\d{11}$')
    email: Optional[EmailStr] 
    city: Optional[str] 
    category_id: Optional[int] = None


class ContactResponse(SQLModel):
    id: int
    name: str
    phone: str
    email: str
    city: str
    category_id: Optional[int] = None
