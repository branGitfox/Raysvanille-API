
from typing import Optional, List
from fastapi import APIRouter, status, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import database
from app.auth import Oauth
from app.database.models import models
from app.database.schemas import schemas
from app.repositories.customerRepository import CustomerRepository
from app.services.customerServices import CustomerServices
from app.utils.utils import  upload_pictures
router = APIRouter(prefix="/customers", tags=["Customers"])

ALLOW_FILE_EXTENSION = ['jpeg', 'png', 'jpg']
PUBLIC_PATH = 'app/uploads/customers'


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_customer(client_name:str = Form(...), notes:str = Form(None), phone:int = Form(...), cin:int = Form(...),  image: Optional[UploadFile] = File(None), db: Session = Depends(database.get_db), current_user: int = Depends(Oauth.get_current_user)):
    CustomerServices.check_if_exist_cin(cin, db)
    new_customer = models.Customer(client_name=client_name, notes=notes, phone=phone, cin=cin)
    new_customer.picture_url = upload_pictures(PUBLIC_PATH, image, ALLOW_FILE_EXTENSION)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return {"message": "Client Créé"}


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.CustomerView])
def get_customers(search:str, promoted:str, reseller:bool, db:Session = Depends(database.get_db), current_user: int = Depends(Oauth.get_current_user)):
    customers_query = db.query(models.Customer).filter(models.Customer.client_name.contains(search.lower()))
    if promoted != "all":
        customers_query = customers_query.filter(models.Customer.is_promoted == (True if promoted == "vip" else False))

    if reseller:
        customers_query = customers_query.filter(models.Customer.is_reseller == reseller)

    customers = customers_query.all()
    return customers


@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.CustomerView)
def get_customer(id:int, db: Session = Depends(database.get_db), current_user: int = Depends(Oauth.get_current_user)):
    return CustomerRepository.find_customer_by_id(id, db)


@router.patch('/promote/{id}', status_code=status.HTTP_202_ACCEPTED)
def promote_customer(id:int, db: Session = Depends(database.get_db), current_user: int = Depends(Oauth.get_current_user)):
    return CustomerServices.promote_customer(id, db)


@router.patch('/notes/{id}', status_code=status.HTTP_202_ACCEPTED)
def save_notes(id:int, content: schemas.CustomerNotes, db: Session = Depends(database.get_db), current_user: int = Depends(Oauth.get_current_user)):
        return CustomerServices.save_notes(id, content.model_dump(), db)


@router.patch('/seller/{id}', status_code= status.HTTP_202_ACCEPTED)
def promote_seller(id: int, db:Session= Depends(database.get_db), current_user: int = Depends(Oauth.get_current_user)):
    return CustomerServices.promote_seller(id, db)

