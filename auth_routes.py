from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException

from werkzeug.security import generate_password_hash , check_password_hash

from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder


from database import Session, engine
from schemas import SignUpModel, SignUpResponseModel, LoginModel
from models import User


auth_router = APIRouter(                                        # creating APIRouter instance

    prefix = '/auth',                                           # route ko prefix(i.e route ko suru ma aaune part) chai /auth rakheko
    tags = ['auth']                                             # auth_router ko sabai routes lai 'auth' vanni tag diyeko

)


session = Session(bind=engine)                                  # session instance create gareko


@auth_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
    """
        ## Hi, this is momo delivery service.
    
    """

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access Token")

    return {"message":"Hi, this is momo delivery service."}





@auth_router.post('/signup', status_code = status.HTTP_201_CREATED, response_model = SignUpResponseModel)
async def signup(user:SignUpModel):
    """
        ## Register/Create a new user.
        This requires the following:
        ```
            username:int
            email:str
            password:str
        ```
    """
    # checking if the email already exists in User table or not.
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail = "User with the email already exists"
        )

    # checking if the username already exists in User table or not.
    db_username = session.query(User).filter(User.username==user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail = "User with the username already exists"
        )

    # creating new user object or instance
    new_user = User(
        username = user.username,
        email = user.email,
        password = generate_password_hash(user.password),
    )

    session.add(new_user)                                   # adding new user to the session
    session.commit()                                        # saving new user object to the database table

    return new_user                                         # finally returning the newly created or registered user





@auth_router.post('/login', status_code= status.HTTP_200_OK)
async def login(user:LoginModel, Authorize:AuthJWT= Depends()):
    """     
        ## Login a user
        This requires
        ```
            username:str
            password:str
        ```
        and returns a token pair, both `access` and `refresh` token. Access token is used for jwt authorization process.
    """
    db_user = session.query(User).filter(User.username == user.username).first()

    # if user exists and password is correct
    if db_user and check_password_hash(db_user.password, user.password):
        access_token = Authorize.create_access_token(subject = db_user.username)
        refresh_token = Authorize.create_refresh_token(subject = db_user.username)

        response = {                                        # response ma both access token and refresh token pathako
            "access": access_token,
            "refresh": refresh_token
        }

        return jsonable_encoder(response)                   # jsonable_encoder() le python dictionary lai JSON ma convert garcha (i.e Django ma )


    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invalid Username Or Password")



# Refreshing the Token (i.e getting access token from refresh token)
@auth_router.get('/refresh')
async def refresh_token(Authorize:AuthJWT= Depends()):
    """
    ## This creates a new access token, so for that, it requires previous refresh token.
    """
    try:
        Authorize.jwt_refresh_token_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Please provide a valid refresh token"
        ) 

    current_user = Authorize.get_jwt_subject()

    # generating access token
    access_token = Authorize.create_access_token(subject=current_user)

    return jsonable_encoder( {"access": access_token} )



