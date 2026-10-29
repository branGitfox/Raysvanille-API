from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.customerRepository import CustomerRepository

class CustomerServices:
    # Modification de note par ID d'un client
    @staticmethod
    def save_notes(customer_id:int, content: dict, db: Session):
        customer_exist =  CustomerRepository.find_customer_by_id(customer_id, db)
        if not customer_exist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce client n'existe pas")
        CustomerRepository.update_customer(customer_id, content, db)
        return {"message": "Notes sauvegardé"}


    # Verifier si la CIN existe deja
    @staticmethod
    def check_if_exist_cin(cin:int, db:Session):
        customer_exist = CustomerRepository.find_customer_by_cin(cin, db)
        if customer_exist:
            raise  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce client existe déjà")


    # Promouvoir un client VIP
    @staticmethod
    def promote_customer(customer_id:int, db: Session):
        customer = CustomerRepository.find_customer_by_id(customer_id, db)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce client existe déjà")
        CustomerRepository.update_customer(customer_id, {"is_promoted":not customer.is_promoted}, db)
        return {"message": f"Client {'promue' if customer.is_promoted else 'retrogradé'}"}


    # Promouvoir en revendeur un client
    @staticmethod
    def promote_seller(customer_id:int, db: Session):
        customer = CustomerRepository.find_customer_by_id(customer_id, db)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce client existe déjà")
        CustomerRepository.update_customer(customer_id, {"is_reseller": not customer.is_reseller}, db)
        return {"message": f"Client {'promue' if customer.is_reseller else 'retrogradé'}"}

