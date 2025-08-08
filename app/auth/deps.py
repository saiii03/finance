from fastapi import Depends,HTTPException,Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.auth.auth import decode_access_token
from app.database import get_db

#dependencies

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="users/login")

def get_current_user(request:Request,db:Session=Depends(get_db)):
    from app.models.user import User
    token=request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401,detail="missing token value")
    
    if token.startswith("Bearer "):
        token=token.split(" ",1)[1]

    
    try:
        payload=decode_access_token(token)
        email:str=payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401,detail="invalid token playload")
    except JWTError:
            raise HTTPException(status_code=401,detail="invalid or expire token")
    

    user=db.query(User).filter(User.email==email).first()
    if user is None:
         raise HTTPException(status_code=401,detail="user not found")
    return user



