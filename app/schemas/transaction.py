from pydantic import BaseModel
from typing import Optional
from datetime import date,datetime

class TransactionBase(BaseModel):
    amount:int
    category:str
    datetime:Optional[date]

class TransactionCreate(BaseModel):
    pass

class TransactionOut(BaseModel):
    id:int
    timestamp:datetime
    user_id=int

class Config:
    orm_mode=True
