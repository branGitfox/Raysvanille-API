from app.database.models import models
from app.database.schemas import schemas
from sqlalchemy.orm import Session
class CategoryRepository:

    @staticmethod
    def find_by_id(category_id:int, db:Session):
        return db.query(models.Category).filter(models.Category.id == category_id).first()