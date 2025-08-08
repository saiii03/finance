from pydantic import BaseModel,confloat
from typing import Optional,Literal
from datetime import datetime

#schemas for transaction[method]
class TransactionBase(BaseModel):
    amount: float  
    category: Optional[str] = None
    type: str  
    date: Optional[datetime] = None 

class TransactionCreate(TransactionBase):
    title: str 
    amount: confloat(gt=0)
    description:str
    type:Literal["income","expense"] 

class TransactionOut(BaseModel):
    id: int
    user_id: int
    title: str
    amount: float
    category: Optional[str]
    type: str
    date: datetime

    class Config:
        orm_mode = True
