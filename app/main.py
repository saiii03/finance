from fastapi import FastAPI, Request,Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.models import user as user_model, transaction as transaction_model
from app.database import engine
from app.routes import user, transaction
from sqlalchemy.orm import Session
from app.auth.deps import get_current_user
from app.database import get_db



user_model.Base.metadata.create_all(bind=engine)
transaction_model.Base.metadata.create_all(bind=engine)

app = FastAPI()


templates = Jinja2Templates(directory="app/templates")


app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(transaction.router,  tags=["transactions"])



@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/")
def read_route():
    return {"message": "welcome to personal finance tracker app"}
