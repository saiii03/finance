from fastapi import APIRouter
from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
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



router=APIRouter()
templates = Jinja2Templates(directory="app/templates")



@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    transactions = db.query(transactionmodel).filter(transactionmodel.user_id == current_user.id).all()

    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    current_balance = total_income - total_expense

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user_email": current_user.email,
            "transactions": transactions,
            "total_income": total_income,   
            "total_expense": total_expense,
            "current_balance": current_balance,
        }
    )

@router.get("/transactions/add",response_class=HTMLResponse)
async def add_transaction_form(
    request:Request,
    db:Session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse("add_transaction.html",{"request":request})

@router.post("/add")
async def add_transaction(
    title: str = Form(...),
    amount: float = Form(...),
    type: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    new_transaction = transactionmodel(
        title=title,
        amount=amount,
        type=type,
        user_id=current_user.id
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)