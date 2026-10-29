from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database.models import models
from app.database.schemas import schemas



class StockServices:
    # Ajout de stock article -> couleur, taille, nombre
    @staticmethod
    def create_stock(content: schemas.StockCreate, db:Session):
        verify_relate = db.query(models.Stock).filter(models.Stock.size_id == content.size_id , models.Stock.color_id == content.color_id , models.Stock.product_id == content.product_id).first()
        if verify_relate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette assemblage de couleur et taille pour ce article existe déjà")

        new_stock = models.Stock(**content.model_dump())
        db.add(new_stock)
        db.commit()


    # Suppression de stock article -> couleur
    @staticmethod
    def remove_stock_color(product_id: int, color_id: int, db: Session):
        query = db.query(models.Stock).filter(models.Stock.color_id == color_id,
                                                       models.Stock.product_id == product_id)
        find_stock = query.first()
        if not find_stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variants non trouvé")
        query.delete(synchronize_session=False)

        db.commit()


    # Supression de article -> taille
    @staticmethod
    def remove_stock_size(product_id: int, size_id: int, color_id:int, db: Session):
        query = db.query(models.Stock).filter(models.Stock.size_id == size_id,models.Stock.product_id == product_id, models.Stock.color_id == color_id)
        find_stock = query.first()
        if not find_stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variants non trouvé")
        query.delete(synchronize_session=False)
        db.commit()