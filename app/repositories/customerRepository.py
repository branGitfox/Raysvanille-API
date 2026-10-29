from sqlalchemy.orm import Session
from ..database.models import models



class CustomerRepository:

    @staticmethod
    def  find_customer_by_id(customer_id:int, db: Session):
        return  (
            db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        )



    @staticmethod
    def  update_customer(customer_id, content: dict, db:Session):
        db.query(models.Customer).filter(models.Customer.id == customer_id).update(content, synchronize_session=False)
        db.commit()


    @staticmethod
    def find_customer_by_cin(cin:int, db:Session):
        return (
            db.query(models.Customer).filter(models.Customer.cin == cin).first()
        )

