from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models import User, UserRegister, UserLogin
from security import hash_password, verify_password, create_token, get_current_user

router = APIRouter()

# register
@router.post("/register", status_code=201)
def register(
    data: UserRegister,
    session: Session = Depends(get_session), #connection to db session
):
    # check username
    existing = session.exec(
        select(User).where(User.username == data.username) #list
    ).first()  

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This user already exists!",
        )

    # build user
    new_user = User(
        username=data.username,
        password=hash_password(data.password),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user) #id

    return {"message": "Successfull Registration!", "user_id": new_user.id}


# login
@router.post("/login")
def login(
    data: UserLogin,
    session: Session = Depends(get_session),
):
    # find user
    user = session.exec(
        select(User).where(User.username == data.username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Username or Passworn is Wrong!",
        )

    # check pass
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Username or Passworn is Wrong!",
        )

    # create token
    token = create_token(user.id)

    return {"token": token, "message": "Welcome!"}

@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
    }
