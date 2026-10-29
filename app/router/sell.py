import json
from typing import List

from fastapi import APIRouter, status, HTTPException, Depends

from sqlalchemy.orm import Session

from  app.database.models import models
from app.database.schemas import schemas
from app.database import database


router = APIRouter(prefix='/sells', tags=['Sells'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_invoices(content: schemas.InvoiceCreation, db: Session = Depends(database.get_db)):
    invoice_count = db.query(models.Invoice).count()
    # creation de la facture
    new_invoice = models.Invoice( portfolio_id = content.portfolio_id , user_id=content.user_id, amount=content.amount, discount=content.discount, customer_name=content.customer_name, customer_id=content.customer_id, payed= content.payed, due_date=content.due_date, sell_type=content.sell_type)
    final_amount = content.amount - content.discount
    new_invoice.final_amount = final_amount
    new_invoice.payed = content.payed
    new_invoice.remains = final_amount - content.payed
    new_invoice.ref = "PLAM"+f"{invoice_count:00}"

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    products = [schemas.InvoiceItem.model_validate(p) for p in json.loads(content.products)]
    for p in products :
        new_items = models.InvoiceItem(**p.model_dump())
        new_items.invoice_id = new_invoice.id
        stock = db.query(models.Stock).filter(models.Stock.color_id == p.color_id, models.Stock.size_id == p.size_id, models.Stock.product_id == p.product_id)
        exist_stock = stock.first()
        if not exist_stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impossible de trouver le stock")
        if exist_stock.count < p.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuffisant")
        stock.update({"count": exist_stock.count - p.quantity})
        db.add(new_items)
    db.commit()
    return {"message":"ok"}



# #  pour la recuperation des facturess
@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.InvoicesView])
def get_invoice(db: Session = Depends(database.get_db)):
    return db.query(models.Invoice).all()
