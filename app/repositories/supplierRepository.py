from sqlalchemy.orm import Session

from app.database.models import models
from app.database.schemas import schemas

class SupplierRepository:

    # rechercher si l'email existe déjà
    @staticmethod
    def exist_email(email:str, db:Session):
        return db.query(models.Supplier).filter(models.Supplier.email == email).first()



    # rechercher si la compagnie  existe déjà
    @staticmethod
    def exist_company(company:str, db:Session):
        return db.query(models.Supplier).filter(models.Supplier.company == company).first()


    # Creation d'un nouveau fournisseur
    @staticmethod
    def create_supplier(content: schemas.SupplierCreate, db:Session):
        new_supplier = models.Supplier(**content.model_dump())
        db.add(new_supplier)
        db.commit()


