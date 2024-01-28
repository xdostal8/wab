from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List

class OrderItemBase(BaseModel):
    item_id: str  # Assuming item_id is a string in your data
    quantity: int
    unit_price: float

class OrderItemCreate(BaseModel):
    item_id: str
    name: str
    quantity: int  # Changed from 'count' to 'quantity'
    unit_price: float  # Changed from 'price_per_unit' to 'unit_price'
    description: str = ""
    category: str = ""
    available: bool = False


class OrderItem(BaseModel):
    item_id: str
    name: str
    quantity: int = Field(alias='count')
    unit_price: float = Field(alias='price_per_unit')
    description: str = None
    category: str = None
    available: bool = True

class OrderBase(BaseModel):
    user_id: str  # Assuming user_id is a string
    total_price: float
    address: str


class OrderCreate(BaseModel):
    user_id: str
    items: List[OrderItemCreate]
    total_price: float
    address: str

class Order(BaseModel):
    user_id: str
    items: List[OrderItem]
    total_price: float
    address: str

    class Config:
        allow_population_by_field_name = True
