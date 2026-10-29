import uuid
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import database
from app.database.models import models
from app.database.schemas import schemas
from app.auth import Oauth

router = APIRouter(prefix="/shop", tags=["Shop"])

# Creation unique ici, je vais encore changer le uuid en simple integer plutard
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_shop(content: schemas.ShopCreate, db: Session = Depends(database.get_db), current_user: int = Depends(Oauth.get_current_user)):
    check_if_already = db.query(models.Shop).all()

    if len(check_if_already) > 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Impossible de créer")

    new_shop = models.Shop(**content.model_dump(), id=uuid.uuid4())
    db.add(new_shop)
    db.commit()
    db.refresh(new_shop)
    return new_shop



@router.get('/', response_model=schemas.Shop, status_code=status.HTTP_200_OK)
def get_shop(db: Session = Depends(database.get_db), current_user: int = Depends(Oauth.get_current_user)):
    get_shop = db.query(models.Shop).first()
    return get_shop



@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def change_shop_config(id:uuid.UUID, content: schemas.ShopCreate, db: Session = Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    shop_query = db.query(models.Shop).filter(models.Shop.id == id)
    shop = shop_query.first()
    if not shop:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration non trouvé")
    shop_query.update(content.model_dump())
    db.commit()
    return {"message": "Information modifié"}


