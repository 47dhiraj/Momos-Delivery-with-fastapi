from pydantic import BaseModel
from typing import Optional


# API through aaune data lai validate garna ko lagi schemas ko use garincha

class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    
    class Config:                                   # configuration
        orm_mode = True                             # by default, orm_mode = False huncha, so orm_mode lai True gareko
        schema_extra = {                            # schema_extra chai khas frontend developer ko lagi sajilo vaos vanera ho
            'example':{
                "username": "test",
                "email": "test@gmail.com",
                "password": "password"
            }
        }



class SignUpResponseModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
	    orm_mode=True



class LoginModel(BaseModel):
    username:str
    password:str

    class Config:
	    orm_mode=True



class Settings(BaseModel):
    authjwt_secret_key:str='4c18e28cad7d39c48de03b935ad3d84299e4787df795f4e61bb3215496f89e37'



class OrderModel(BaseModel):
    id: Optional[int]
    plate_quantity: int
    order_status: Optional[str]="PENDING"
    momo_size: Optional[str]="MEDIUM"
    user_id: Optional[int]


    class Config:
        orm_mode = True
        schema_extra= {
            "example":{
                "plate_quantity":1,
                "momo_size":"MEDIUM"
            }
        }



class OrderStatusModel(BaseModel):
    order_status: Optional[str]="PENDING"

    class Config:
        orm_mode=True
        schema_extra={
            "example":{
                "order_status": "PENDING"
            }
        }


