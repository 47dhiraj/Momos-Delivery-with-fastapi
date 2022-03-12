from database import engine, Base
from models import User, Order                          # yesari model use navaye pani models lai import garnai parcha, natra database ma table create hudaina


Base.metadata.create_all(bind = engine)                   # this line actually creates the tables in database


