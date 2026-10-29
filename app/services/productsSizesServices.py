from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import models
from app.database.schemas import schemas



class ProductsSizesServices:
    # Creer la relation article -> taille et couleur
    @staticmethod
    def create_products_sizes(content: schemas.ProductsSizes, db:Session):
        verify_relate = db.query(models.ProductsSizes).filter(models.ProductsSizes.size_id == content.size_id, models.ProductsSizes.product_id == content.product_id, models.ProductsSizes.color_id==content.color_id).first()
        if verify_relate:
            pass
        else:
            new_products_sizes = models.ProductsSizes(**content.model_dump())
            db.add(new_products_sizes)
            db.commit()


    # Supprimer la relation article -> taille et couleur
    @staticmethod
    def remove_variant_size(product_id:int, size_id:int, color_id:int,  db:Session):
        query = db.query(models.ProductsSizes).filter(models.ProductsSizes.size_id == size_id, models.ProductsSizes.product_id==product_id, models.ProductsSizes.color_id == color_id)
        find_product_size = query.first()
        if not find_product_size:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taille non trouvée")
        query.delete(synchronize_session=False)

        db.commit()