from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder

from database import Session, engine
from models import User, Order
from schemas import OrderModel, OrderStatusModel



order_router = APIRouter(

    prefix = "/orders",                                         # route ko prefix(i.e route ko suru ma aaune part) chai /orders rakheko
    tags = ['orders']                                           # order_router ko sabai routes lai 'orders' vanni tag diyeko

)

session = Session(bind=engine)                                  # creating session instance # session instance ko help batw database table lai query garna sakincha


@order_router.get('/')
async def hello():
    """
        ## Hi, this is momo delivery service.
    """
    try:
        Authorize.jwt_required()                               # jwt authentication required vaneko

    except Exception as e:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid Token"
        )

    return {"message": "Hi, this is momo delivery service."}



@order_router.post('/orders', status_code = status.HTTP_201_CREATED)
async def place_an_order(order:OrderModel, Authorize:AuthJWT = Depends()):
    """
        ## Placing an Order
        This requires the following
        - plate_quantity : integer
        - momo_size: str
    
    """
    try:
        Authorize.jwt_required()                                # jwt authentication required cha vaneko

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    current_user = Authorize.get_jwt_subject()                  # get_jwt_subject() le current logged in user ko information dincha

    user = session.query(User).filter(User.username == current_user).first()    # user instance lai fetch garera nikaleko

    new_order = Order(                                          # creating new order instance
        momo_size = order.momo_size,
        plate_quantity = order.plate_quantity
    )

    new_order.user = user                                       # attaching the order to the current logged in user

    session.add(new_order)
    session.commit()                                            # order lai database table ma save gareko

    response = {                                                # response dictionary
        "momo_size": new_order.momo_size,
        "plate_quantity": new_order.plate_quantity,
        "id": new_order.id,
        "order_status": new_order.order_status
    }

    return jsonable_encoder(response)                           # response dictionary lai JSON format ma lageko



@order_router.get('/orders', status_code= status.HTTP_200_OK)
async def list_all_orders(Authorize:AuthJWT = Depends()):
    """
        ## List all orders
        Only Superuser of Staff can access list of all orders.
    """
    try:
        Authorize.jwt_required()                                # jwt authentication required cha vaneko

    except Exception as e:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    current_user = Authorize.get_jwt_subject()                  # get_jwt_subject() le current logged in user ko information dincha
    user = session.query(User).filter(User.username == current_user).first() # fetching the user from database

    if user.is_staff:                                           # staff or superuser le matra orders herna paune
        orders = session.query(Order).all()
        return jsonable_encoder(orders)

    raise  HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "You are not a superuser"
        )



@order_router.get('/orders/{id}', status_code= status.HTTP_200_OK)
async def get_order_by_id(id:int, Authorize:AuthJWT = Depends()):
    """
        ## Get an order by its ID
        Order detail can only be viewed by superuser and it takes order id in url.
    """
    try:
        Authorize.jwt_required()                                # Authorizatio required cha vaneko

    except Exception as e:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid Token"
        )


    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:                                   # superuser or staff le matra order ko detail herna paucha
        order = session.query(Order).filter(Order.id == id).first()
        return jsonable_encoder(order)


    raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Your are not authorized user"
        )




@order_router.get('/user/orders', status_code= status.HTTP_200_OK)
async def get_user_orders(Authorize:AuthJWT = Depends()):
    """
        ## Get a current user's orders
        The list of orders made by the currently logged in users.
    """
    try:
        Authorize.jwt_required()                                # Authorized user checking gareko

    except Exception as e:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    return jsonable_encoder(current_user.orders)                # current_user.orders vannale, current logged in user ko orders haru 



@order_router.get('/user/order/{id}/', status_code= status.HTTP_200_OK)
async def get_specific_order(id:int, Authorize:AuthJWT = Depends()):
    """
        ## Get a specific order by the currently logged in user
        This returns a particular order made by the currently logged in user. It takes id as url parameter.
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()
    orders = current_user.orders                        # logged in user ko matra orders suru ma fetch gareko

    for o in orders:
        if o.id == id:                                  #  particular user ko orders haru madhye pani, particular order lai fetch gareko 
            return jsonable_encoder(o)
    
    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
        detail = "Requested order not found."
    )



@order_router.put('/order/update/{id}/', status_code= status.HTTP_200_OK)
async def update_order(id:int, order:OrderModel, Authorize:AuthJWT = Depends()):
    """
        ## Updating an order
        This udates an order and requires the following fields
        - plate_quantity : integer
        - momo_size: str
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    order_to_update = session.query(Order).filter(Order.id == id).first()

    # update garne wala value rakhidai cha
    order_to_update.plate_quantity = order.plate_quantity
    # order_to_update.order_status = order.order_status         # only staff can update the order status so tei vayera yo line lai comment nai garako
    order_to_update.momo_size = order.momo_size
    session.commit()                                            # update garna ko lagi session.add() garna pardaina, just session.commit() gare huncha


    response = {
                "id": order_to_update.id,
                "plate_quantity": order_to_update.plate_quantity,
                "momo_size": order_to_update.momo_size,
                "order_status": order_to_update.order_status,
            }

    return jsonable_encoder(order_to_update)



@order_router.patch('/order/update/{id}/', status_code= status.HTTP_200_OK)             # partial data or specific field ko data matra update garne vaye patch request use garda pani huncha
async def update_order_status(id: int, order: OrderStatusModel, Authorize: AuthJWT = Depends()):
    """
        ## Update an order's status
        This is for updating an order's status and only requires 'order_status' in str format.
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    username = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == username).first()

    if current_user.is_staff:                                       # staff or superuse ho vani matra status update garna paucha
        order_to_update = session.query(Order).filter(Order.id == id).first()
        order_to_update.order_status = order.order_status
        session.commit()                                            # update garna ko lagi session.add() gari rakhna pardaina, just session.commit() gare huncha

        response = {
                "id": order_to_update.id,
                "plate_quantity": order_to_update.plate_quantity,
                "momo_size": order_to_update.momo_size,
                "order_status": order_to_update.order_status,
            }

        return jsonable_encoder(response)



@order_router.delete('/order/delete/{id}/', status_code = status.HTTP_204_NO_CONTENT)
async def delete_an_order(id:int, Authorize:AuthJWT = Depends()):
    """
        ## Delete an Order
        This deletes an order by id.
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid Token")

    order_to_delete = session.query(Order).filter(Order.id == id).first()
    session.delete(order_to_delete)
    session.commit()

    return order_to_delete


