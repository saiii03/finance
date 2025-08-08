from fastapi import Depends,HTTPException,status,APIRouter
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from app.models.transaction import Transaction as Transactionmodel
from app.schemas.transaction import  TransactionCreate,TransactionOut
from app.auth.deps import get_current_user
from app.models.user import User


# api for transaction

router=APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

@router.get('/',response_model=List[TransactionOut])
def get_transactions(
    db:Session=Depends(get_db),
    current_user: User=Depends(get_current_user),
):
    transactions=db.query(Transactionmodel).filter(Transactionmodel.user_id == current_user.id).all()
    return transactions

@router.get('/{transaction_id}',response_model=TransactionOut)
def get_transaction(
    transaction_id:int,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user),
):
    transaction=db.query(Transactionmodel).filter(Transactionmodel.id == transaction_id,Transactionmodel.user_id==current_user.id).first()
    if not transaction:
        raise HTTPException(status_code=404,detail="transaction not found")
    return transaction
    
@router.delete('/{transaction_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id:int,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user),
):
    transaction=db.query(Transactionmodel).filter(Transactionmodel.id == transaction_id,Transactionmodel.user_id==current_user.id).first()
    if not transaction:
        raise HTTPException(status_code=404,detail="transaction not found")
    db.delete(transaction)
    db.commit()
    return 
@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_transaction = Transactionmodel(
        amount=abs(transaction.amount),
        description=transaction.description,
        type=transaction.type,
        user_id=current_user.id,
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


