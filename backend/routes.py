from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, or_, select
from typing import Optional
from database import get_session
from models import (
    Contact, ContactCreate, ContactUpdate, ContactResponse,
    Category, CategoryCreate, User,
)
from security import get_current_user

router = APIRouter()


# ============ Category ============

@router.post("/categories", status_code=201)
def create_category(
    data: CategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    category = Category(
        name=data.name,
        user_id=current_user.id,
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.get("/categories")
def get_categories(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(Category).where(Category.user_id == current_user.id)
    return session.exec(query).all()


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category Not Found!")

    contacts = session.exec(
        select(Contact).where(Contact.category_id == category_id)
    ).all()
    for c in contacts:
        c.category_id = None
        session.add(c)

    session.delete(category)
    session.commit()
    return {"message": "Category Deleted!"}


# ============ Contact ============

def check_duplicate(session: Session, phone: str, email: str, user_id: int, exclude_id: int = None):
    query = select(Contact).where(
        (Contact.phone == phone) | (Contact.email == email)
    ).where(Contact.user_id == user_id)
    if exclude_id is not None:
        query = query.where(Contact.id != exclude_id)
    existing = session.exec(query).first()
    if existing:
        if existing.email == email:
            raise HTTPException(status_code=400, detail="Email already exists.")
        if existing.phone == phone:
            raise HTTPException(status_code=400, detail="Phone number already exists.")


@router.get("/contacts")
def get_contacts(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(Contact).where(Contact.user_id == current_user.id)

    if search:
        query = query.where(or_(
            Contact.name.contains(search),
            Contact.phone.contains(search),
            Contact.email.contains(search),
            Contact.city.contains(search),
        ))

    if category_id is not None:
        query = query.where(Contact.category_id == category_id)

    total = len(session.exec(query).all())
    query = query.offset(skip).limit(limit)
    contacts = session.exec(query).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": contacts,
    }


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    contact = session.get(Contact, contact_id)
    if not contact or contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not Found!")
    return contact


@router.post("/contacts", status_code=201, response_model=ContactResponse)
def create_contact(
    data: ContactCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
  
    check_duplicate(session, data.phone, data.email, current_user.id)

    if data.category_id is not None:
        category = session.get(Category, data.category_id)
        if not category or category.user_id != current_user.id:
            raise HTTPException(status_code=400, detail="This Category is invalid!")

    new_contact = Contact(
        name=data.name,
        phone=data.phone,
        email=data.email,
        city=data.city,
        user_id=current_user.id,
        category_id=data.category_id,   
    )
    session.add(new_contact)
    session.commit()
    session.refresh(new_contact)
    return new_contact


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    data: ContactUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    contact = session.get(Contact, contact_id)
    if not contact or contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not Found!")

    new_phone = data.phone if data.phone is not None else contact.phone
    new_email = data.email if data.email is not None else contact.email
    check_duplicate(session, new_phone, new_email, current_user.id, exclude_id=contact_id)

    if data.name is not None:
        contact.name = data.name
    if data.phone is not None:
        contact.phone = data.phone
    if data.email is not None:
        contact.email = data.email
    if data.city is not None:
        contact.city = data.city
    if data.category_id is not None:
        category = session.get(Category, data.category_id)
        if not category or category.user_id != current_user.id:
            raise HTTPException(status_code=400, detail="Category is invalid!")
        contact.category_id = data.category_id

    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


@router.delete("/contacts/{contact_id}")
def delete_contact(
    contact_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    contact = session.get(Contact, contact_id)
    if not contact or contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not Found")
    session.delete(contact)
    session.commit()
    return {"message": "Deleted"}
