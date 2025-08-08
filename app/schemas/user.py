from pydantic import BaseModel,EmailStr

#schemas for user section[methods]

class UserBase(BaseModel):
    email:EmailStr

class UserCreate(UserBase):
    password:str

class UserOut(BaseModel):
    id:int
    email:EmailStr
    class Config:
        orm_mode=True
        form_attributes=True


class Token(BaseModel):
    access_token: str
    token_type:str

class Tokendata(BaseModel):
    email:EmailStr|None=None