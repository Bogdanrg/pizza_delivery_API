from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from core.database import get_db
from fastapi_jwt_auth import AuthJWT
from models import Order
from schemas import OrderModel, OrderStatusModel
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from services.auth_service import jwt_required, get_user_by_username, super_user_required

order_router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@order_router.get('/')
async def hello(Authorize: AuthJWT = Depends()):
    jwt_required(Authorize)
    return jsonable_encoder("hello")


@order_router.post('/order', status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    jwt_required(Authorize)

    current_user = Authorize.get_jwt_subject()
    user = get_user_by_username(db, current_user)
    new_order = Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity,
        user=user
    )

    db.add(new_order)
    db.commit()

    return jsonable_encoder({
        'id': new_order.id,
        'pizza_size': new_order.pizza_size,
        'quantity': new_order.quantity,
        'order_status': new_order.order_status
    })


@order_router.get('/orders')
async def list_all_orders(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    jwt_required(Authorize)
    super_user_required(Authorize, db)
    orders = db.query(Order).all()
    return jsonable_encoder(orders)


@order_router.get('/orders/{order_id}')
async def retrieve_order(order_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    jwt_required(Authorize)
    super_user_required(Authorize, db)
    current_user = Authorize.get_jwt_subject()
    user = get_user_by_username(db, current_user)

    order = db.query(Order).filter(Order.id == order_id).first()

    return jsonable_encoder({
        'id': order.id,
        'pizza_size': order.pizza_size,
        'quantity': order.quantity,
        'order_status': order.order_status,
        'user': order.user.username
    })


@order_router.get('/user/orders')
async def get_user_orders(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    jwt_required(Authorize)

    current_user = Authorize.get_jwt_subject()
    user = get_user_by_username(db, current_user)
    orders = db.query(Order).filter(user.id == Order.user_id).all()
    return jsonable_encoder(orders)


@order_router.get('/user/order/{order_id}')
async def get_user_order(order_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    jwt_required(Authorize)
    current_user = Authorize.get_jwt_subject()
    user = get_user_by_username(db, current_user)
    orders = db.query(Order).filter(user.id == Order.user_id).all()
    for order in orders:
        if order.id == order_id:
            return jsonable_encoder(order)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No orders with such id"
    )


@order_router.put('/order/update/{order_id}')
async def update_order(order_id: int, order_instance: OrderModel, Authorize: AuthJWT = Depends(),
                       db: Session = Depends(get_db)):
    jwt_required(Authorize)
    current_user = Authorize.get_jwt_subject()
    user = get_user_by_username(db, current_user)
    order = db.query(Order).filter(Order.id == order_id).first()
    if order not in user.orders:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have such an order")
    order.quantity = order_instance.quantity
    order.pizza_size = order_instance.pizza_size

    db.commit()
    return jsonable_encoder(order)


@order_router.patch('/order/status/{order_id}')
async def update_order_status(order_id: int, order: OrderStatusModel, Authorize: AuthJWT = Depends(),
                              db: Session = Depends(get_db)):
    jwt_required(Authorize)
    super_user_required(Authorize, db)
    order_to_update = db.query(Order).filter(Order.id == order_id).first()
    order_to_update.order_status = order.order_status

    db.commit()
    return jsonable_encoder(order_to_update)
