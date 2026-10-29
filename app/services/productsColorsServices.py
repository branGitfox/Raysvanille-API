from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import models
from app.database.schemas import schemas


class ProductsColorsServices:

    # Creer la relation article -> couleur
    @staticmethod
    def create_products_colors(content: schemas.ProductsColors, db: Session):
        verify_relate = db.query(models.ProductsColors).filter(
            models.ProductsColors.color_id == content.color_id , models.ProductsColors.product_id == content.product_id).first()
        if verify_relate:
            pass
        else:
            new_products_colors = models.ProductsColors(**content.model_dump())
            db.add(new_products_colors)
            db.commit()


    # Supprimer la relation artile -> couleur
    @staticmethod
    def remove_variant_color(product_id:int, color_id:int,  db:Session):
        query = db.query(models.ProductsColors).filter(models.ProductsColors.color_id == color_id, models.ProductsColors.product_id==product_id)
        find_product_colors = query.first()
        if not find_product_colors:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couleur non trouvé")
        query.delete(synchronize_session=False)

        db.commit()



