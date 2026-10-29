from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.database import database
from app.database.models import models
from app.database.schemas import schemas
from sqlalchemy.orm import Session

router  = APIRouter(prefix='/depenses', tags=['Depenses'])


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.DepensesView])
def get_depenses(db: Session = Depends(database.get_db)):
    return db.query(models.Depense).all()



@router.post('/', status_code=status.HTTP_201_CREATED)
def get_depenses(content: schemas.DepenseCreation, db: Session = Depends(database.get_db)):
    portfolio_query = db.query(models.Portfolio).filter(models.Portfolio.id == content.portfolio_id)
    find_portfolio = portfolio_query.first()
    if not find_portfolio:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Le portfeuille n'existe pas")
    # verification du solde
    total_cost = content.amount
    if find_portfolio.balance < total_cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Le solde du  portfeuille est insuffisant")
    portfolio_query.update({"balance": find_portfolio.balance - total_cost})
    new_depense = models.Depense(**content.model_dump())
    db.add(new_depense)

    db.commit()
    return {"message": "Depense enregistré"}