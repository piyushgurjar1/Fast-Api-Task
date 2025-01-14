from sqlalchemy.orm import Session
import models, schemas

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_menu_items(db: Session):
    return db.query(models.MenuItem).all()

def create_menu_item(db: Session, item: schemas.MenuItemCreate):
    db_item = models.MenuItem(name=item.name, description=item.description, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(status='Pending', user_id=order.user_id, menu_item_id=order.menu_item_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, user_id: int = None):
    if user_id:
        return db.query(models.Order).filter(models.Order.user_id == user_id).all()
    return db.query(models.Order).all()

def update_order_status(db: Session, order_id: int, status: str):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        db_order.status = status
        db.commit()
        db.refresh(db_order)
        return db_order
    return None


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()