from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.repositories.categoryRepository import CategoryRepository


class CategoryServices:


    # Recuperation de nom de categorie par ID
    @staticmethod
    def get_category_name(category_id:int, db:Session) -> str:
        category = CategoryRepository.find_by_id(category_id, db)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category non trouvé")
        return category.category_name