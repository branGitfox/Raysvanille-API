from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from pip._internal.cli import status_codes
from sqlalchemy.orm import Session
from app.database.schemas import schemas
from app.database.models import models
from app.database import database
from app.auth import Oauth
router = APIRouter(prefix="/sizes", tags=["Sizes"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_size(content: schemas.SizeCreate, db: Session = Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    is_unique  = db.query(models.Size).filter(models.Size.size_name == content.size_name).first()
    if is_unique:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette taille existe déjà")

    new_size = models.Size(**content.model_dump())
    db.add(new_size)
    db.commit()
    return {"message": "Taille créée"}


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.Size])
def get_all(db: Session = Depends(database.get_db),  current_user:int=Depends(Oauth.get_current_user)):
    return db.query(models.Size).all()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_size(id:int, db:Session=Depends(database.get_db),  current_user:int=Depends(Oauth.get_current_user)):
    query = db.query(models.Size).filter(models.Size.id == id)
    size = query.first()
    if not size:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taille non trouvé")
    query.delete(synchronize_session=False)
    db.commit()
    return {"message":"Taille supprimé"}


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_size(id:int, content: schemas.SizeCreate,  db:Session=Depends(database.get_db),  current_user:int=Depends(Oauth.get_current_user)):
    query = db.query(models.Size).filter(models.Size.id == id)
    size = query.first()
    if not size:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taille non trouvé")
    query.update(content.model_dump(), synchronize_session=False)
    db.commit()
    return {"message": "Taille modifié"}


