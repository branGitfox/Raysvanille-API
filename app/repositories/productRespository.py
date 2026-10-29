from sqlalchemy.orm import Session

from app.database import database
from app.database.models import models
from app.database.schemas import schemas



class ProductRepository:
    # rechercher un produit par ID
    @staticmethod
    def find_by_id(product_id:int, db:Session):
        return db.query(models.Product).filter(models.Product.id == product_id).first()


    # rechercher un produit par brand
    @staticmethod
    def find_by_brand(product_brand:str, db:Session):
        return db.query(models.Product).filter(models.Product.brand == product_brand).first()


    # compter articles par categorie
    @staticmethod
    def count_by_category(category_id:int, db:Session):
        return len(db.query(models.Product).filter(models.Product.category_id == category_id).all()) + 1


    # creation d'un nouveau article
    @staticmethod
    def create_product(brand:str,category_id:int ,genre_id:int,description:str,price:int,purchase_price:int,min_stock:int,
        code:str,
        is_new:bool,
        is_available:bool,
        image_url:str, db:Session):
        new_product = models.Product(
            brand=brand,
            category_id=category_id,
            genre_id=genre_id,
            description=description,
            price=price,
            purchase_price=purchase_price,
            min_stock=min_stock,
            code=code,
            is_new=is_new,
            is_available=is_available,
            image_url=image_url
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product


    # pour la modification d'un article existant
    @staticmethod
    def update_product(product_id:int, content: dict, db:Session):
        db.query(models.Product).filter(models.Product.id == product_id).update(content, synchronize_session=False)
        db.commit()


    # pour supprimer un produit par son id
    def delete_product(product_id:int, db:Session):
        db.query(models.Product).filter(models.Product.id == product_id).delete(synchronize_session=False)
        db.commit()


