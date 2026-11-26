import json
from email.message import EmailMessage
from typing import List


from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import database
from app.database.schemas import schemas
from app.database.models import models
from app.utils.utils import send_test_email, send_queued_mail

router = APIRouter(prefix='/orders', tags=["Orders"])


# pour la creation d'une commande
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_orders(content: schemas.OrderCreation, background_tasks: BackgroundTasks, db:Session = Depends(database.get_db)):
    user = None
    if content.type == "auth":
        user_exist = db.query(models.Customer).filter(models.Customer.email == content.email).first()
        user = user_exist
        if not user_exist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impossible de valider cette commande, Session refusé")
    else:
        user_exist = db.query(models.Customer).filter(models.Customer.email == content.email).first()
        user = user_exist
        if not user_exist:
            new_customer = models.Customer(client_name=content.customer_name, picture_url="https://userplaceholder", email=content.email)
            db.add(new_customer)
            db.commit()
            user = db.query(models.Customer).filter(models.Customer.email == content.email).first()

    order_count = db.query(models.Orders).count()
    code = f"#RV-{order_count*10000}"
    new_orders = models.Orders(phone=content.phone, customer_name=content.customer_name, city = content.city, code = code, localisation=content.localisation, total_purchase=content.total_purchase, status="pending", customer_id=user.id, description=content.description)
    db.add(new_orders)

    db.commit()
    db.refresh(new_orders)
    items = [schemas.OrderItemCreation.model_validate(v) for v in json.loads(content.items)]
    for item in items:
        new_order_item = models.OrderItem(item_name=item.item_name, quantity=item.quantity, tag=item.tag)
        new_order_item.order_id = new_orders.id
        db.add(new_order_item)
        db.commit()
    # je dois envoyer un mali ici, je dois encor pesonnaliser le template ici

    await send_queued_mail(    "order_received", content.email, content.customer_name, background_tasks,
    order_id=new_orders.code,
    items=items,
    total=content.total_purchase,
    cta_url=f"http://57.128.67.164/account/orders",
    links=[("Contactez-nous", "http://57.128.67.164/#contact")],)
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
async def update_order_status(order_id:int, content: schemas.StatusUpdate, background_tasks: BackgroundTasks,  db:Session = Depends(database.get_db)):
    query = db.query(models.Orders).filter(models.Orders.id == order_id)
    verify_order = query.first()
    if not verify_order:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail= " impossible de trouver la commande")
    query.update({"status": content.status }, synchronize_session= False)
    db.commit()
    customer = db.query(models.Customer).filter(models.Customer.id == verify_order.customer_id).first()
    if content.status == "confirmed":
        await send_queued_mail("order_confirmed", customer.email, verify_order.customer_name,background_tasks, order_id=verify_order.code,total=verify_order.total_purchase )
    else:
        await send_queued_mail("order_cancelled", customer.email, verify_order.customer_name,background_tasks, order_id=verify_order.code,total=verify_order.total_purchase )

    return {"message": " Status de commande modifié"}


# pour l'envoie des emails
def send_email():
    pass


