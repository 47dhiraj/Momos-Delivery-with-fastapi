from database import Base
from sqlalchemy import Column, Integer, Boolean, Text, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType



class User(Base):                                                       # User Model or Table

    __tablename__= 'user'
    id = Column(Integer, primary_key = True)
    username = Column(String(50), unique = True)
    email = Column(String(70), unique = True)
    password = Column(Text, nullable = False)
    is_staff = Column(Boolean, default = False)
    is_active = Column(Boolean, default = False)

    orders = relationship('Order', back_populates = 'user')             # back_populates = 'user', yo user vanni relational field Order table ma huna parcha  # Establishing Relationship  

    def __repr__(self):
        return f"<User {self.username}"



class Order(Base):                                                      # Order Model or Table

    ORDER_STATUS = (                                                    # Choice Types
        ('PENDING','pending'),
        ('IN-TRANSIT','in-transit'),
        ('DELIVERED','delivered')
    )

    MOMO_SIZES = (
        ('SMALL','small'),
        ('MEDIUM','medium'),
        ('LARGE','large')
    )

    __tablename__= 'orders'
    id = Column(Integer, primary_key = True)
    plate_quantity = Column(Integer, nullable = False)
    order_status = Column(ChoiceType(choices = ORDER_STATUS), default = "PENDING")
    momo_size = Column(ChoiceType(choices = MOMO_SIZES), default = "MEDIUM")

    user_id = Column(Integer, ForeignKey('user.id'))                    # ForeignKey represents One to Many Relationship

    user = relationship('User', back_populates = 'orders')              # Establishing Relationship

    def __repr__(self):
        return f"<Order {self.id}>"


