from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from typing import List
from .rabbitmq import publish
from . import schemas, crud, database, models
from .database import SessionLocal, engine
from sqlalchemy.orm import sessionmaker
import pika
import json
import threading


def process_order(order_data):
    db = SessionLocal()
    try:
        # Start a new transaction
        db.begin()

        # Create a new Order object
        new_order = models.Order(
            user_id=order_data["user_id"],
            total_price=order_data["total_price"],
            address=order_data["address"]
        )
        db.add(new_order)
        # Flush to get the new order ID without committing yet
        db.flush()

        # Create OrderItem objects
        for item_data in order_data["items"]:
            new_order_item = models.OrderItem(
                order_id=new_order.id,  # Use the generated ID from the new Order
                item_id=item_data["item_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"]
            )
            db.add(new_order_item)

        # Commit the transaction after all items have been added
        db.commit()
        print(f"Order processed: {new_order.id}")

    except Exception as e:
        print(f"Error processing order: {e}")
        # Roll back the transaction on error
        db.rollback()
    finally:
        db.close()


# RabbitMQ consumer setup in a separate function
def start_rabbitmq_consumer():
    conn_params = pika.ConnectionParameters(
    host='rabbitmq',
    credentials=pika.PlainCredentials('user', 'secret')
)
    conn = pika.BlockingConnection(conn_params)
    channel = conn.channel()
    channel.queue_declare(queue="orders", durable=True)

    def on_message_callback(channel, method, properties, body):
        print(f"""
        channel:   {channel}
        method:    {method}
        properties:{properties}
        body:      {body}""")
        print(f"Received Order: {body}")
        order_data = json.loads(body)
        process_order(order_data)

    channel.basic_consume(queue="orders", on_message_callback=on_message_callback, auto_ack=True)
    print("Starting consuming...")
    channel.start_consuming()

# Start RabbitMQ consumer in a separate thread
threading.Thread(target=start_rabbitmq_consumer, daemon=True).start()



models.Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    conn_params = pika.ConnectionParameters(
        host='rabbitmq',
        credentials=pika.PlainCredentials('user', 'secret')
    )
    conn = pika.BlockingConnection(conn_params)
    channel = conn.channel()
    channel.queue_declare(queue="orders", durable=True)

    def on_message_callback(channel, method, properties, body):
        print(f"""
            channel:   {channel}
            method:    {method}
            properties:{properties}
            body:      {body}""")
        print(f"Received Order: {body}")
        order_data = json.loads(body)
        process_order(order_data)

    channel.basic_consume(queue="orders", on_message_callback=on_message_callback, auto_ack=True)
    print("Starting consuming...")
    channel.start_consuming()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
async def homepage(request: Request):
    # User is not logged in
    html_content = '''
    <html>
        <head>
            <title>Home Page</title>
        </head>
        <body>
            <h1>Welcome to the orders</h1>
            <a href="/orders">reviews</a><br>
        </body>
    </html>
    '''
    return HTMLResponse(content=html_content)

@app.post("/orders", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.insert_order(db=db, order=order)

@app.get("/orders", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders
