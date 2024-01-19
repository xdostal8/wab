from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class OrderItem(BaseModel):
    itemId: UUID
    quantity: int
    price: float

class PostOrder(BaseModel):
    store_id: UUID
    user_id: UUID
    name: str
    surname: str
    phone: str
    address: str
    items: List[OrderItem]

class Order(PostOrder):
    id: UUID
    created: datetime