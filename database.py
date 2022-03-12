from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Database engine for MySQL database
engine = create_engine('mysql://root:@localhost/momo_api',
    echo=True
)

# # Database engine for postgresql database
# engine = create_engine('postgresql://postgres:password@localhost/momo_api',
#     echo=True
# )


Base = declarative_base()

Session = sessionmaker()                        # sessionmaker object helps to do perform CRUD query in the database

