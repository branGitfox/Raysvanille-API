from typing import List
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from app.repositories.productRespository import ProductRepository
from app.services.categoryServices import CategoryServices
from app.utils import utils
from app.database.schemas import schemas
import json
from app.services.productsSizesServices import ProductsSizesServices
from app.services.productsColorsServices import ProductsColorsServices
from app.services.stockServices import StockServices

class ProductServices:

    # rechercher un article par son ID
    @staticmethod
    def find_product_by_id(product_id:int, db:Session):
        product =  ProductRepository.find_by_id(product_id, db)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article non trouvé")
        return product

    # verifier si la brand (nom de l'article) existe deja
    @staticmethod
    def check_if_exist_brand(brand:str, db:Session):
        product =  ProductRepository.find_by_brand(brand, db)
        if product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cet articles existe déjà")


    # Verifier si les prix (achat et vente) sont > à 0
    @staticmethod
    def check_if_prices_ok(price:int, purchase_price:int):
        if price <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le prix doit > 0")
        if purchase_price <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le prix d'achat > 0")


    # pour generer dynamiquement un code pour chaque produit par rapport à son categorie
    @staticmethod
    def generate_product_code(category_id:int, db:Session) -> str:
        category_name = CategoryServices.get_category_name(category_id, db)
        product_count =  ProductRepository.count_by_category(category_id, db)
        random_code = str(category_name[0:2]).upper() + str(category_name[-1]).upper() + "-" + f"{product_count:010}"
        return random_code


    # pour gerer la creation d'un produit complet
    @staticmethod
    def create_product(public_path:str, allowed_extension:List[str], is_new:bool, is_available:bool, variants: str , brand:str, category_id:int, genre_id:int, description:str, price:int, purchase_price:int,
                   min_stock:int, image:UploadFile, db:Session):
        ProductServices.check_if_exist_brand(brand, db)
        ProductServices.check_if_prices_ok(price, purchase_price)
        random_code = ProductServices.generate_product_code(category_id, db)
        image_url = utils.upload_pictures(public_path, image, allowed_extension)
        new_product = ProductRepository.create_product(brand, category_id, genre_id, description, price, purchase_price, min_stock, random_code, is_new, is_available, image_url, db)
        variants = [
            schemas.Variants.model_validate(v)
            for v in json.loads(variants)
        ]
        for v in variants:
            ProductsSizesServices.create_products_sizes(
                schemas.ProductsSizes(product_id=new_product.id, size_id=v.size_id, color_id=v.color_id), db)
            ProductsColorsServices.create_products_colors(
                schemas.ProductsColors(product_id=new_product.id, color_id=v.color_id), db)
            StockServices.create_stock(
                schemas.StockCreate(product_id=new_product.id, color_id=v.color_id, size_id=v.size_id, count=v.stock),
                db)
        return {"message":"Article créé"}


    # Modification d'un produit
    @staticmethod
    def update_product(public_path:str, allowed_file_extension:List[str],product_id:int, is_new:bool, is_available:bool, brand:str, category_id:int, genre_id:int, description:str, price:int, purchase_price:int, min_stock:int, image:UploadFile, db:Session):
        find_product = ProductServices.find_product_by_id(product_id, db)
        utils.remove_old_pictures(image, find_product.image_url)
        image_url = find_product.image_url if image is None else utils.upload_pictures(public_path, image,                                                                        allowed_file_extension)
        ProductRepository.update_product(product_id,{
        "brand": brand,
        "is_new": is_new,
        "category_id": category_id,
        "genre_id": genre_id,
        "description": description,
        "price": price,
        "purchase_price": purchase_price,
        "min_stock": min_stock,
        "image_url": image_url,
        "is_available":is_available}, db)
        return {"message": "Article modifié"}


    # Suppression d'un produit
    @staticmethod
    def delete_product(product_id:int, db:Session):
        find_product = ProductServices.find_product_by_id(product_id, db)
        utils.remove_pictures(find_product.image_url)
        ProductRepository.delete_product(product_id, db)
