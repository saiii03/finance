from fastapi import APIRouter,requests,Request
from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from sqlalchemy import func

from app.database import get_db
from fastapi import Form,Request
from app.auth.deps import get_current_user
from app.models.transaction import Transaction as transactionmodel
from fastapi import Form



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
    request: Request,
    title: str = Form(...),
    amount: float = Form(...),
    type: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")
    
    amount = abs(amount)

    # Only run this if it's an expense
    if type == "expense":
        total_income = db.query(func.sum(transactionmodel.amount)).filter(
            transactionmodel.user_id == current_user.id,
            transactionmodel.type == "income"
        ).scalar() or 0

        total_expense = db.query(func.sum(transactionmodel.amount)).filter(
            transactionmodel.user_id == current_user.id,
            transactionmodel.type == "expense"
        ).scalar() or 0

        current_balance = total_income - total_expense

        if current_balance - amount < 0:
            return templates.TemplateResponse("add_transaction.html", {
                "request": request,
                "warning": f"❌ Insufficient balance. Your current balance is ${current_balance:.2f}, but you're trying to spend ${amount:.2f}.",
                "title": title,
                "amount": amount,
                "type": type
            })

    # Create and save the transaction
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

@router.post('/transactions/delete')
async def delete_transaction_post(
    transaction_id:int=Form(),
    db:Session=Depends(get_db),
    current_user=Depends(get_current_user),
):
    transaction=db.query(transactionmodel).filter(
        transactionmodel.id==transaction_id,
        transactionmodel.user_id==current_user.id,
    ).first()

    if not transaction :
        raise HTTPException(status_code=401,detail="transaction not found")
    
    db.delete(transaction)
    db.commit()
    return RedirectResponse(url='/dashboard',status_code=status.HTTP_303_SEE_OTHER)