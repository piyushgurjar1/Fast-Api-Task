from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base  
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default='user')
    orders = relationship('Order', back_populates='user')


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, default='')
    price = Column(Integer)
    orders = relationship('Order', back_populates='menu_item')

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default='Pending')
    user_id = Column(Integer, ForeignKey('users.id'))
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'))
    user = relationship('User', back_populates='orders')
    menu_item = relationship('MenuItem', back_populates='orders')