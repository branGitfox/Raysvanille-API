from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.orm import Session
from app.database import database
from app.database.schemas import schemas
from app.database.models import models
from app.auth import Oauth
router = APIRouter(prefix='/portfolios', tags=['Portfolios'])


# Creation d'un portfolio
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_portfolio(content:schemas.PortfolioCreate, db: Session = Depends(database.get_db),  current_user:int=Depends(Oauth.get_current_user)):
    find_portfolio = db.query(models.Portfolio).filter(models.Portfolio.portfolio_name == content.portfolio_name).first()
    if find_portfolio:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette portefeuille existe déjà")
    new_portfolio = models.Portfolio(**content.model_dump())
    db.add(new_portfolio)
    db.commit()
    return {"message": "Portefeuille créée"}


# Recuperation liste de portfolio
@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.PortfolioView])
def get_portfolios(db:Session=Depends(database.get_db),  current_user:int=Depends(Oauth.get_current_user)):
    return db.query(models.Portfolio).all()
