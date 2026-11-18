import json
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import database
from app.database.schemas import schemas
from app.database.models import models

router = APIRouter(prefix='/orders', tags=["Orders"])


# pour la creation d'une commande
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_orders(content: schemas.OrderCreation, db:Session = Depends(database.get_db)):
    user_exist = db.query(models.Customer).filter(models.Customer.email == content.email).first()
    if not user_exist:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impossible de valider cette commande, Session refusé")
    order_count = db.query(models.Orders).count()
    code = f"#RV-{order_count:000000}"
    new_orders = models.Orders(phone=content.phone, customer_name=content.customer_name, city = content.city, code = code, localisation=content.localisation, total_purchase=content.total_purchase, status="pending", customer_id=user_exist.id)
    db.add(new_orders)

    db.commit()
    db.refresh(new_orders)
    items = [schemas.OrderItemCreation.model_validate(v) for v in json.loads(content.items)]
    for item in items:
        new_order_item = models.OrderItem(item_name=item.item_name, quantity=item.quantity, tag=item.tag)
        new_order_item.order_id = new_orders.id
        db.add(new_order_item)
        db.commit()
    return {"message": "commande envoyée", "code": new_orders.code}


@router.get('/', response_model=List[schemas.OrderView], status_code=status.HTTP_200_OK)
def get_orders(db:Session=Depends(database.get_db)):
    orders = db.query(models.Orders).all()
    return orders



@router.get('/{email}', response_model=List[schemas.OrderView], status_code=status.HTTP_200_OK)
def get_orders_by_email(email:str,db:Session=Depends(database.get_db)):
    customer = db.query(models.Customer).filter(models.Customer.email ==email).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No session")
    orders = db.query(models.Orders).filter(models.Orders.customer_id==customer.id).all()
    return orders

# Ppour le changement de status de commande

@router.put('/{order_id}', status_code=status.HTTP_202_ACCEPTED)
def update_order_status(order_id:int, content: schemas.StatusUpdate,  db:Session = Depends(database.get_db)):
    query = db.query(models.Orders).filter(models.Orders.id == order_id)
    verify_order = query.first()
    if not verify_order:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail= " impossible de trouver la commande")
    query.update({"status": content.status }, synchronize_session= False)
    db.commit()
    return {"message": " Status de commande modifié"}


# pour l'envoie des emails
def send_email():
    pass


