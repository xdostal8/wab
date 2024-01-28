from sqlalchemy.orm import Session
from . import models, schemas
from uuid import uuid4

def insert_order(db: Session, order: schemas.OrderCreate) -> models.Order:
    db_order = models.Order(
        user_id=order.user_id,
        total_price=order.total_price,
        address=order.address
    )
    db.add(db_order)
    db.flush()  # This will assign an ID to db_order without committing the transaction

    for item in order.items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            item_id=item.item_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        db.add(db_item)
    
    db.commit()
    return db_order


def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()
