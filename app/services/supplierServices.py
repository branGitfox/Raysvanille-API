from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from app.database.schemas import schemas
from app.repositories.supplierRepository import SupplierRepository


class SupplierServices:

    # Verification si l'email existe déjà
    @staticmethod
    def exist_email(email:str, db:Session):
        supplier = SupplierRepository.exist_email(email, db)
        if supplier:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet email existe déjà")


    # Verification si la compagnie existe déjà
    @staticmethod
    def exist_company(company:str, db:Session):
        company = SupplierRepository.exist_company(company, db)
        if company:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce fournisseur existe déjà")


    # Creation d'un nouveau fournisseur
    @staticmethod
    def create_supplier(content: schemas.SupplierCreate, db:Session):
        # SupplierServices.exist_email(content.email, db)
        SupplierServices.exist_company(content.company, db)
        SupplierRepository.create_supplier(content, db)
        return {"message": "Fournisseur créé"}