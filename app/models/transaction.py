from sqlalchemy import Column, Integer, Float, ForeignKey,String
from sqlalchemy.orm import relationship
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    category = Column(String)
    type = Column(String)  
    date = Column(String)

user=relationship("User",back_populates="transactions")
