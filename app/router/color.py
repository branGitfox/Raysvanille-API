from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database.schemas import schemas
from app.database.models import models
from app.database import database
from app.auth import Oauth
router = APIRouter(prefix="/colors", tags=["Colors"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_color(content: schemas.ColorCreate, db: Session = Depends(database.get_db),  current_user:int=Depends(Oauth.get_current_user)):
    is_unique  = db.query(models.Color).filter(models.Color.color_name == content.color_name).first()
    if is_unique:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette couleur existe déjà")

    new_color = models.Color(**content.model_dump())
    db.add(new_color)
    db.commit()
    return {"message": "Couleur créée"}


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.Color])
def get_all(db: Session = Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    return db.query(models.Color).all()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_color(id:int, db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    query = db.query(models.Color).filter(models.Color.id == id)
    color = query.first()
    if not color:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couleur non trouvé")
    query.delete(synchronize_session=False)
    db.commit()
    return {"message":"Couleur supprimé"}


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_color(id:int, content: schemas.ColorCreate,  db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    query = db.query(models.Color).filter(models.Color.id == id)
    color = query.first()
    if not color:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couleur non trouvé")
    query.update(content.model_dump(), synchronize_session=False)
    db.commit()
    return {"message": "Couleur modifié"}

