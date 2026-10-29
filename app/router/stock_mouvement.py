from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.orm import Session
from app.database import database
from app.database.schemas import schemas
from app.database.models import models
from app.auth import Oauth
router = APIRouter(prefix='/stock-movements', tags=['Stocks', 'Mouvements'])

# Approvisionnement d'article
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_stock_mouvement(content: schemas.StockMouvementCreate, db:Session=Depends(database.get_db), current_user:int=Depends(Oauth.get_current_user)):
    # Doit verifier si existe stocks
    query = db.query(models.Stock).filter(models.Stock.size_id==content.size_id, models.Stock.color_id==content.color_id, models.Stock.product_id==content.product_id)
    find_stock = query.first()
    if not find_stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Les variantes n'existes pas ou a été supprimées")
    # recuperer le portfeuille
    portfolio_query = db.query(models.Portfolio).filter(models.Portfolio.id == content.portfolio_id)
    find_portfolio = portfolio_query.first()
    if not find_portfolio:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Le portfeuille n'existe pas")
    # verification du solde
    total_cost = content.quantity * content.unit_cost
    if find_portfolio.balance < total_cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Le solde du  portfeuille est insuffisant")
    portfolio_query.update({"balance": find_portfolio.balance - total_cost})
    new_stmouv = models.StockMovement(**content.model_dump(), ref="ENT-001", total_cost = total_cost)
    query.update({"count": find_stock.count + content.quantity}, synchronize_session=False)
    db.add(new_stmouv)
    new_depenses = models.Depense(user_id=current_user, portfolio_id=find_portfolio.id, amount=total_cost, description="Approvisionnement d'article Ref#")
    db.add(new_depenses)
    db.commit()
    return {"message":"Approvisionnement reussi"}


# Recuperer l'historique d'approvisionnements
@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.StockMouvementShow])
def get_history(db:Session=Depends(database.get_db),  current_user:int=Depends(Oauth.get_current_user)):
    return db.query(models.StockMovement).order_by(models.StockMovement.created_at.desc()).all()




# # approvisionnement de solde d'un portfolio pour le test
# @router.get('/appro')
# def appro(db:Session=Depends(database.get_db)):
#     db.query(models.Portfolio).filter(models.Portfolio.id == 1).update({"balance":1000000}, synchronize_session=False)
#     db.commit()
#     return {"message": "Approvisionnement reussi !"}


# pour faire une transaction entre portfeuille
@router.post("/trans", status_code=201)
def transaction(content: schemas.TransactionCreation, db: Session = Depends(database.get_db)):
    # verifier si les portfeuilles existent ou pas
    from_query = db.query(models.Portfolio).filter(models.Portfolio.id == content.p_from)
    to_query = db.query(models.Portfolio).filter(models.Portfolio.id == content.p_to)
    p_from = from_query.first()
    if not p_from:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce portfeuille n'existe pas")

    p_to = to_query.first()
    if not p_to:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce portfeuille n'existe pas")

    # verification des soldes
    p_from_balance = p_from.balance
    p_to_balance = p_to.balance


    if p_from_balance < content.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solde insuffisant")

    # Declenchement du transfert
    from_query.update({"balance": p_from.balance - content.amount}, synchronize_session=False)
    to_query.update({"balance": p_to_balance + content.amount}, synchronize_session=False)

    # archivage de la transaction
    transac = models.Transaction(**content.model_dump())
    db.add(transac)
    db.commit()
    return {"message": "La transaction est reussi"}


"""

    JE  ME SUIS TROMPE DE ROUTER ICI, JE DOIS DEPLACER DANS UN AUTRE ROUTER PLUTARD "PORTFOLIO", CAR C'EST PAS TRES CLEAN
    
"""

# récuperation des historiques de transfert
@router.get('/history', status_code=status.HTTP_200_OK, response_model=List[schemas.TransactionHistory])
def get_history(db: Session=Depends(database.get_db)):
    history = db.query(models.Transaction).all()
    return history


# pour l'approvisionnement d'une portfeuille
@router.post("/supply", status_code=status.HTTP_202_ACCEPTED)
def supply(content: schemas.PortfolioSupply, db: Session = Depends(database.get_db)):
    query = db.query(models.Portfolio).filter(models.Portfolio.id == content.portfolio_id)
    portfolio = query.first()
    if content.amount == 0:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Insérerz un montnat > 0")
    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portefeuille introuvable")
    query.update({"balance": portfolio.balance + content.amount}, synchronize_session=False)
    history = models.PortfolioSupplyHistory(amount=content.amount, date=content.date, portfolio_id=content.portfolio_id)
    db.add(history)

    db.commit()
    return {"message": "Approvisionnement Reussi !"}


# pour recupere les historiques d'approvisionnemnts
@router.get("/supply/{portfolio_id}", response_model = List[schemas.PortfolioSupplyHistoryCreation], status_code=status.HTTP_200_OK)
def get_supply_history(portfolio_id:int, db: Session = Depends(database.get_db)):
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
    portfolio_history = db.query(models.PortfolioSupplyHistory).filter(models.PortfolioSupplyHistory.portfolio_id == portfolio_id).all()

    if not portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impossible de trouver la portefeuille")
    return portfolio_history











