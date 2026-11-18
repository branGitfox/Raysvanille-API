from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import database
from app.database.models import models
from app.database.schemas import schemas

router = APIRouter(prefix="/content", tags=["Content"])

CONTENT_ID = 1  # ligne unique


def get_or_404(db: Session) -> models.Content:
    content = db.query(models.Content).filter(models.Content.id == CONTENT_ID).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Le contenu du site n'a pas encore été créé",
        )
    return content


# Public : la vitrine en a besoin
@router.get("/", response_model=schemas.ContentOut)
def get_content(db: Session = Depends(database.get_db)):
    return get_or_404(db)


# Création unique (id=1) : 409 si elle existe déjà
@router.post("/", response_model=schemas.ContentOut, status_code=status.HTTP_201_CREATED)
def create_content(
    payload: schemas.ContentCreate,
    db: Session = Depends(database.get_db),
    # current_user = Depends(oauth2.get_current_user),   # <- à protéger comme vos autres routes admin
):
    if db.query(models.Content).filter(models.Content.id == CONTENT_ID).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Le contenu existe déjà, utilisez PUT pour le modifier",
        )
    content = models.Content(id=CONTENT_ID, **payload.model_dump())  # Pydantic v1: .dict()
    db.add(content)
    try:
        db.commit()
    except IntegrityError:  # deux POST simultanés
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Le contenu existe déjà, utilisez PUT pour le modifier",
        )
    db.refresh(content)
    return content


# Modification de la ligne unique
@router.put("/", response_model=schemas.ContentOut)
def update_content(
    payload: schemas.ContentUpdate,
    db: Session = Depends(database.get_db),
    # current_user = Depends(oauth2.get_current_user),
):
    content = get_or_404(db)
    for field, value in payload.model_dump().items():  # Pydantic v1: .dict()
        setattr(content, field, value)
    db.commit()
    db.refresh(content)
    return content