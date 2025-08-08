from fastapi import APIRouter, Depends, Request, status, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import get_db
from app.auth.deps import get_current_user
from app.models.transaction import Transaction as transactionmodel
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# categories of income and expenses
VALID_INCOME_CATEGORIES = ["Salary", "Bonus", "Investment", "Reimbursement", "Others"]
VALID_EXPENSE_CATEGORIES = ["Rent", "Food", "Travel", "Utilities", "Others"]


#main dashboard backend 
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    type:str=Query("all"),
    category:Optional[str]=Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query= db.query(transactionmodel).filter(transactionmodel.user_id == current_user.id)
    if type in ("income","expense"):
        query=query.filter(transactionmodel.type==type)
    if category:
        query=query.filter(transactionmodel.category==category)
    transactions=query.order_by(transactionmodel.date.desc()).all()


    all_txns=db.query(transactionmodel).filter(transactionmodel.user_id==current_user.id).all()
    total_income = sum(t.amount for t in all_txns if t.type == "income")
    total_expense = sum(t.amount for t in all_txns if t.type == "expense")
    current_balance = total_income-total_expense

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user_email": current_user.email,
            "transactions": transactions,
            "total_income": total_income,
            "total_expense": total_expense,
            "current_balance": current_balance,
            "VALID_INCOME_CATEGORIES":VALID_INCOME_CATEGORIES,
            "VALID_EXPENSE_CATEGORIES":VALID_EXPENSE_CATEGORIES,
            "SELECTED_CATEGORIES":category,
            "SELECTED_TYPE":type,
            
        }
    )

# get transaction to use transaction button

@router.get("/transactions/add", response_class=HTMLResponse)
async def add_transaction_form(
    request: Request,
    type: Optional[str] = Query("income"),  
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    categories = VALID_INCOME_CATEGORIES if type == "income" else VALID_EXPENSE_CATEGORIES

    return templates.TemplateResponse("add_transaction.html", {
        "request": request,
        "type": type,
        "category": None,
        "categories": categories,
        "title": "",
        "amount": "",
        "description": "",
    })

#post transaction to put the input and helps with category

@router.post("/add")
async def add_transaction(
    request: Request,
    title: str = Form(...),
    amount: float = Form(...),
    type: str = Form(...),
    category: str = Form(...),
    description: str = Form(''),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    if type == "income" and category not in VALID_INCOME_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid income category")
    if type == "expense" and category not in VALID_EXPENSE_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid expense category")

    amount = abs(amount)

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
            categories = VALID_EXPENSE_CATEGORIES
            return templates.TemplateResponse("add_transaction.html", {
                "request": request,
                "warning": f"Insufficient balance. Your current balance is ${current_balance:.2f}, but you're trying to spend ${amount:.2f}.",
                "title": title,
                "amount": amount,
                "type": type,
                "category": category,
                "categories": categories,
                "description": description,
            })

    new_transaction = transactionmodel(
        title=title,
        amount=amount,
        type=type,
        category=category,
        description=description,
        user_id=current_user.id,
        datetime=datetime,
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

#

@router.post('/transactions/delete')
async def delete_transaction_post(
    transaction_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    transaction = db.query(transactionmodel).filter(
        transactionmodel.id == transaction_id,
        transactionmodel.user_id == current_user.id,
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
    return RedirectResponse(url='/dashboard', status_code=status.HTTP_303_SEE_OTHER)








