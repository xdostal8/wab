from fastapi import APIRouter, Depends, Request

from .database import db
from .models import Item, Cart, CartItem
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json
from bson import json_util




router = APIRouter()

templates = Jinja2Templates(directory="templates")



def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user



@router.get('/items', response_class=HTMLResponse)
async def get_items(request: Request, user: dict = Depends(get_current_user)):
    items = list(db['items'].find())
    return templates.TemplateResponse("items.html", {"request": request, "items": items, "user": user})


@router.get('/items/category/{category_name}')
async def get_items_by_category(category_name: str) -> list[Item]:
    query = {"category": category_name}
    return list(db['items'].find(query))


@router.post('/new-item', status_code=201)
async def post_item(item: Item):
    response = db['items'].insert_one(item.dict())
    return {"id": str(response.inserted_id)}

from bson import ObjectId

@router.put('/item/{item_id}', status_code=200)
async def update_item(item_id: str, item: Item):
    # Convert the item_id to an ObjectId for querying
    query = {"_id": ObjectId(item_id)}

    # Update the item
    response = db['items'].replace_one(query, item.dict())

    if response.modified_count == 1:
        return {"message": "Item updated successfully"}
    else:
        # Handle case where item does not exist
        return {"error": "Item not found or no update made"}

@router.delete('/item/{item_id}', status_code=200)
async def delete_item(item_id: str):
    # Convert the item_id to an ObjectId for querying
    query = {"_id": ObjectId(item_id)}

    # Delete the item
    response = db['items'].delete_one(query)

    if response.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    else:
        # Handle case where item does not exist
        return {"error": "Item not found"}
    
    # Manage carts
@router.post('/cart/add', status_code=201)
async def add_to_cart(cart: Cart):
    # Check if the user's cart already exists
    existing_cart = db['carts'].find_one({"user_id": cart.user_id})

    if existing_cart:
        # Update existing cart
        db['carts'].update_one({"user_id": cart.user_id}, {"$set": {"items": cart.items}})
        return {"message": "Cart updated"}
    else:
        # Create new cart
        db['carts'].insert_one(cart.dict())

        return {"message": "Cart created"}

from fastapi import HTTPException

from fastapi.encoders import jsonable_encoder

@router.get('/cart', response_class=HTMLResponse)
async def get_cart(request: Request, user: dict = Depends(get_current_user)):
    user_id = user['sub']
    cart = db['carts'].find_one({"user_id": user_id})
    if not cart:
        cart = {"user_id": user_id, "items": [], "total_price": 0.0}
    else:
        # Serialize the cart, including ObjectId fields
        cart = json.loads(json_util.dumps(cart))

        print(cart)  # Debug: Print the cart structure


    return templates.TemplateResponse("cart.html", {"request": request, "user": user, "cart": cart})






from fastapi import HTTPException


@router.delete('/cart')
async def clear_cart(request: Request, user: dict = Depends(get_current_user)):
    user_id = user['sub'] 
    # Retrieve the cart
    cart = db['carts'].find_one({"user_id": user_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Iterate over items in the cart and update inventory
    for cart_item in cart['items']:
        item_id = cart_item['item_id']
        quantity = cart_item['count']
        
        # Retrieve the item from the database
        item = db['items'].find_one({"_id": ObjectId(item_id)})
        if item:
            new_count = item['count'] + quantity
            new_reserved = item['reserved'] - quantity
            db['items'].update_one({"_id": ObjectId(item_id)}, {"$set": {"count": new_count, "reserved": new_reserved}})

    # Delete the cart after restoring item counts
    db['carts'].delete_one({"user_id": user_id})
    return {"message": "Cart cleared and items restored"}


@router.post('/cart/item/add/{item_id}/{quantity}', status_code=201)
async def add_item_to_cart(item_id: str, quantity: int, user: dict = Depends(get_current_user)):
    user_id = user['sub'] 
    item = db['items'].find_one({"_id": ObjectId(item_id)})
    if not item or item['count'] < quantity:
        raise HTTPException(status_code=400, detail="Item not available or insufficient stock")

    # Update the item count in the inventory
    db['items'].update_one({"_id": ObjectId(item_id)}, {"$set": {"count": item['count'] - quantity}})

    # Update the cart
    cart = db['carts'].find_one({"user_id": user_id})
    if cart:
        # Check if item is already in the cart
        existing_item = next((i for i in cart['items'] if i['item_id'] == item_id), None)
        if existing_item:
            existing_item['quantity'] += quantity
        else:
            # Construct a CartItem with full item details
            cart_item = CartItem(
                item_id=item_id,
                name=item['name'],
                count=quantity,  # Note: count here refers to quantity in cart
                reserved=item['reserved'],
                price_per_unit=item['price_per_unit'],
                description=item['description'],
                category=item['category'],
                available=item['available']
            ).dict()
            cart['items'].append(cart_item)
        db['carts'].update_one({"user_id": user_id}, {"$set": {"items": cart['items']}})
    else:
        # Create new cart
        new_cart = Cart(user_id=user_id, items=[CartItem(
            item_id=item_id,
            name=item['name'],
            count=quantity,  # Note: count here refers to quantity in cart
            reserved=item['reserved'],
            price_per_unit=item['price_per_unit'],
            description=item['description'],
            category=item['category'],
            available=item['available']
        ).dict()])
        db['carts'].insert_one(new_cart.dict())
    return {"message": "Item added to cart"}

