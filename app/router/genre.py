from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database.schemas import schemas
from app.database.models import models
from app.database import database
from app.auth import Oauth
router = APIRouter(prefix="/genres", tags=["Genres"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_genre(content: schemas.GenreCreate, db: Session = Depends(database.get_db),  current_user:int=Depends(Oauth.get_current_user)):
    is_unique  = db.query(models.Genre).filter(models.Genre.genre_name == content.genre_name).first()
    if is_unique:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette genre existe déjà")

    new_genre = models.Genre(**content.model_dump())
    db.add(new_genre)
    db.commit()
    return {"message": "Genre créée"}


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.Genre])
def get_all(db: Session = Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    return db.query(models.Genre).all()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_genre(id:int, db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    query = db.query(models.Genre).filter(models.Genre.id == id)
    genre= query.first()
    if not genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre non trouvé")
    query.delete(synchronize_session=False)
    db.commit()
    return {"message":"Genre supprimé"}


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update_genre(id:int, content: schemas.GenreCreate,  db:Session=Depends(database.get_db)):
    query = db.query(models.Genre).filter(models.Genre.id == id)
    genre = query.first()
    if not genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre non trouvé")
    query.update(content.model_dump(), synchronize_session=False)
    db.commit()
    return {"message": "Genre modifié"}


