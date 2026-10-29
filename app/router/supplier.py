from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import database
from app.database.models import models
from app.database.schemas import schemas
from app.services.supplierServices import SupplierServices
from app.auth import Oauth
router = APIRouter(prefix='/suppliers', tags=['Suppliers'])

# Creation d'un nouveau fournisseur
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_supplier(content:schemas.SupplierCreate, db:Session = Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    return SupplierServices.create_supplier(content, db)


# Recuperation de tout les fournisseurs
@router.get('/', response_model=List[schemas.SupplierShow], status_code=status.HTTP_200_OK)
def get_all(search:str='',db:Session= Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    suppliers = db.query(models.Supplier).filter(models.Supplier.supplier_name.contains(search.lower()) | models.Supplier.company.contains(search.lower())).all()

    return suppliers


# Modificcation d'un fournisseur par ID
@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_supplier(id:int, content: schemas.SupplierEdit , db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):

    # verifier si company n'existe pas encore
    exist_company = db.query(models.Supplier).filter(models.Supplier.company == content.company, models.Supplier.id != id).first()
    exist_email = db.query(models.Supplier).filter(models.Supplier.supplier_name == content.supplier_name, models.Supplier.id != id).first()
    if exist_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet email existe déjà")
    if exist_company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce fournisseur existe déjà")
    query = db.query(models.Supplier).filter(models.Supplier.id == id)
    find_supplier = query.first()
    if not find_supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce fournisseur n'existe pas")
    query.update(content.model_dump(), synchronize_session=False)
    db.commit()
    return {"message": "Fournisseur modifié"}


# Suppression d'un fournisseur
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(id:int, db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    query = db.query(models.Supplier).filter(models.Supplier.id == id)
    find_supplier = query.first()
    if not find_supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce fournisseur n'existe pas")
    query.delete(synchronize_session=False)
    db.commit()



