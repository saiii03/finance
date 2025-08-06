from fastapi import APIRouter


router=APIRouter()


@router.get('/')
def get_transaction():
    return {"message":"List Of Transactions"}

@router.post('/')
def create_transaction():
    return{"message":"Transaction has been created"+1}