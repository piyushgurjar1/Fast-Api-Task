from fastapi import FastAPI, Depends,status,Response,HTTPException
from sqlalchemy.orm import Session
import schemas, utils, crud, models 
from database import engine, SessionLocal, Base
from passlib.context import CryptContext
from typing import List
from fastapi.security import OAuth2PasswordBearer


Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db=db, username=request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not utils.verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = utils.create_access_token(data={"sub": user.username, "role": user.role})
    return schemas.LoginResponse(access_token=access_token)



@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash_password(user.password)
    return crud.create_user(db=db, user=user)


@app.get("/menu/", response_model=List[schemas.MenuItem])
def get_menu_items( db: Session = Depends(get_db)):
    return crud.get_menu_items(db=db)

@app.post("/menu/", response_model=schemas.MenuItem)
def create_menu_item(item: schemas.MenuItemCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        user_data = utils.verify_token(token)
        role = user_data.get("role")
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action"
            )
    except HTTPException as e:
        raise e 

    return crud.create_menu_item(db=db, item=item)


@app.put("/menu/{menu_id}/", response_model=schemas.MenuItem)
def update_menu_item(
    menu_id: int, 
    item: schemas.MenuItemCreate, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    try:
        user_data = utils.verify_token(token)
        role = user_data.get("role")
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action"
            )
    except HTTPException as e:
        raise e  
    
    db_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with id {menu_id} not found"
        )

    db_item.name = item.name
    db_item.description = item.description
    db_item.price = item.price
    db.commit()
    db.refresh(db_item)
    
    return db_item


@app.delete("/menu/{menu_id}/", response_model=schemas.MenuItem)
def delete_menu_item(
    menu_id: int, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    try:
        user_data = utils.verify_token(token)
        role = user_data.get("role")
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action"
            )
    except HTTPException as e:
        raise e  

    db_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with id {menu_id} not found"
        )

    db.delete(db_item)
    db.commit()

    return db_item


@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

@app.get("/orders/", response_model=List[schemas.Order])
def get_orders(user_id: int = None, db: Session = Depends(get_db)):
    return crud.get_orders(db=db, user_id=user_id)

@app.post("/orders/{order_id}/status/", response_model=schemas.Order)
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = crud.update_order_status(db=db, order_id=order_id, status=status)
    return order

