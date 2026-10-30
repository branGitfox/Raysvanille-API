
from typing import List, Optional
import json
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Depends
from pygments.styles import default

from app.utils import utils
from app.auth import Oauth
from app.database import database
from app.database.models import models
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.services.productsSizesServices import ProductsSizesServices
from app.services.productsColorsServices import ProductsColorsServices
from app.services.stockServices import StockServices
from app.services.productServices import  ProductServices
from app.database.schemas import schemas



router = APIRouter(tags=["Products"])

ALLOW_FILE_EXTENSION = ['jpeg', 'png', 'jpg']
PUBLIC_PATH = 'app/uploads/products'

# Creation d'un article
@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(tags:str = Form(...) , description : str=Form(...), stock : int = Form(...), p_status : str = Form(...),  brand:str=Form(...), category_id:int=Form(...), price:int=Form(...),
                    images:list[UploadFile]=File(None), db:Session=Depends(database.get_db), current_user:int = Depends(database.get_db)):
    verify_redondance = db.query(models.Product).filter(models.Product.brand == brand).first()
    if verify_redondance:
        raise HTTPException(status_code =status.HTTP_400_BAD_REQUEST, detail="Ce nom de produit existe deja")
    new_product = models.Product(description=description, stock=stock,status = p_status, brand=brand, category_id = category_id, price = price, last_price=price, min_stock=3)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    for image in images:
        image_url = utils.upload_pictures(PUBLIC_PATH, image, ALLOW_FILE_EXTENSION)
        new_image = models.Images(product_id = new_product.id, image_url=image_url)
        db.add(new_image)
        db.commit()
    tags_list = [schemas.Tags.model_validate(tag) for tag in json.loads(tags)]
    for tag in tags_list:
        new_tag = models.Tag(tag_name=tag.tag_name, quantity=tag.quantity, product_id = new_product.id)
        db.add(new_tag)
        db.commit()
    return "ok"

# Recuperation des articles avec recherche
@router.get("/products", status_code=status.HTTP_200_OK, response_model = List[schemas.ProductView])
def get_all(search: Optional[str]="",category:Optional[int]=0, genre:Optional[int]=0,stock:Optional[str]="all", limit:Optional[int]=0, db:Session=Depends(database.get_db), ):
    products = db.query(models.Product).all()

    return products


# Recuperation d'un seul produit par ID
@router.get('/products/{id}', status_code=status.HTTP_200_OK, response_model=schemas.ProductEdit)
def get_product(id:int, db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    return ProductServices.find_product_by_id(id, db)


# Recuperation des stocks par combinaison (size_id, color_id, count)
@router.get('/products/stocks/{id}', status_code=status.HTTP_200_OK, response_model=List[schemas.StockView])
def get_stock(id:int, db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    ProductServices.find_product_by_id(id, db)
    stocks = db.query(models.Stock).filter(models.Stock.product_id == id).all()
    return stocks





# Ajout de nouveau de combinaison (size_id, color_id, count)
@router.post('/products/stocks', status_code=status.HTTP_201_CREATED)
def add_stock(content: schemas.AddSStock, db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    ProductServices.find_product_by_id(content.id, db)
    variants = [
        schemas.VariantsEdit.model_validate(v) for v in json.loads(content.variants)
    ]
    for v in variants:
        ProductsSizesServices.create_products_sizes(schemas.ProductsSizes(product_id=content.id, size_id=v.size_id, color_id=v.color_id), db)
        ProductsColorsServices.create_products_colors(schemas.ProductsColors(product_id=content.id, color_id=v.color_id), db)
        StockServices.create_stock(schemas.StockCreate(product_id=content.id, color_id=v.color_id, size_id=v.size_id, count=v.count),db)


# Modification d'un article par ID
@router.put('/products/{id}', status_code=status.HTTP_202_ACCEPTED)
def edit_product(id:int,is_new:bool=Form(...), is_available:bool=Form(...), brand:str=Form(...), category_id:int=Form(...), genre_id:int=Form(...), description:str=Form(""), price:int=Form(...), purchase_price:int=Form(...), min_stock:int=Form(...), image:UploadFile=File(None), db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    return ProductServices.update_product(PUBLIC_PATH, ALLOW_FILE_EXTENSION, id, is_new, is_available, brand, category_id, genre_id, description, price, purchase_price, min_stock, image, db)


# Suppression d'un article par ID
@router.delete('/products/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id:int , db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    ProductServices.delete_product(id, db)


# Suppression d'une variante de couleur
@router.delete('/products/colors/{product_id}/{color_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_variant_color(product_id:int, color_id:int, db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    ProductsColorsServices.remove_variant_color(product_id, color_id, db)
    StockServices.remove_stock_color(product_id, color_id, db)


# Suppression d'une taille
@router.delete('/products/stocks/{product_id}/{size_id}/{color_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_variant_stock(product_id:int, size_id:int, color_id:int, db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    ProductsSizesServices.remove_variant_size(product_id, size_id, color_id, db)
    # si il reste qu'un seule taille on supprime la couleur completement
    check_if_exist = len(db.query(models.Stock).filter(models.Stock.color_id == color_id,models.Stock.product_id == product_id).all()) <= 1
    if check_if_exist:
        ProductsColorsServices.remove_variant_color(product_id, color_id, db)
    StockServices.remove_stock_size(product_id, size_id, color_id, db)




