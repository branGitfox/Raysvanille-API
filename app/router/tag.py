from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.models import models
# from app.database.schemas import schemas
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
    return {"message": "tag supprimé"}


