from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionBase(BaseModel):
    amount: float  
    category: Optional[str] = None
    type: str  
    date: Optional[datetime] = None  
class TransactionCreate(TransactionBase):
    title: str  

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
