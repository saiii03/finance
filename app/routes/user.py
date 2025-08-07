from fastapi import APIRouter, Depends, Request, status, HTTPException,Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.responses import RedirectResponse

from app.models import user as user_model
from app.database import get_db
from app.utils import verify_password, hash_password
from app.auth.auth import create_access_token 
from app.schemas import user as user_schema
from fastapi import Form,Request
from app.auth.deps import get_current_user
from app.models.transaction import Transaction as transactionmodel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

templates = Jinja2Templates(directory="app/templates")


@router.post("/register")
def register(
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
    ):
        existing_user = db.query(user_model.User).filter(user_model.User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_pwd = hash_password(password)
        new_user = user_model.User(email=email, hashed_password=hashed_pwd)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": new_user.id, "email": new_user.email}



@router.post('/login', response_model=user_schema.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(user_model.User).filter(user_model.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="invalid email or password")
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True,path='/')
    return response

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
        return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
        return templates.TemplateResponse("register.html", {"request": request})


@router.post('/logout')
def logout():
      response=RedirectResponse(url='/users/login',status_code=status.HTTP_303_SEE_OTHER)
      response.delete_cookie(key="access_token")
      return response

