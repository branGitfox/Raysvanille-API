import uuid

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.models import models
from app.database.schemas import schemas
from app.database import database

router = APIRouter(prefix="/tags", tags=['Tags'])



@router.delete('/{tag_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id:int, db:Session = Depends(database.get_db)):
    query = db.query(models.Tag).filter(models.Tag.id == tag_id)
    check_if_exist_tag = query.first()
    if not check_if_exist_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Tag introuvable")
    query.delete(synchronize_session=False)
    db.commit()




@router.post('/{product_id}', status_code=status.HTTP_201_CREATED)
def add_tag(product_id: uuid.UUID, tag:schemas.Tags, db:Session=Depends(database.get_db)):
    verify_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not verify_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="impossible de trouver le produit")
    new_tag = models.Tag(**tag.model_dump())
    new_tag.product_id = product_id
    db.add(new_tag)
    db.commit()
    return {"message": "Tag ajouté"}



