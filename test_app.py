import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
import models, crud, schemas
import main,utils

SQLALCHEMY_DATABASE_URL = "sqlite:///.memory.db" 
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture
def create_test_user(test_db):
    user_data = {
        "username": "pisy",
        "password": "1234"
    }
    user = crud.create_user(test_db, user=schemas.UserCreate(**user_data))
    return user


def test_create_user(test_db, create_test_user):
    response = crud.get_user_by_username(test_db, username=create_test_user.username)
    assert response.username == create_test_user.username  
    assert response.password == create_test_user.password   

 
def test_login_invalid_credentials(test_db):
    login_data = {
        "username": "abcd",
        "password": "123"
    }
    response = crud.get_user_by_username(test_db, username=login_data["username"])
    assert response == None



def test_create_menu_item(client: TestClient, test_db):
    login_data = {
        "username": "piy",
        "password": "123"
    }
    access_token = utils.create_access_token(data={"sub": login_data["username"], "role": "admin"})
    
    menu_item_data = {
        "name": "Pizza",
        "description": "Cheese Pizza",
        "price": 10
    }

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.post("/menu/", json=menu_item_data, headers=headers)

    assert response.status_code == 200
    created_item = response.json()

    assert "name" in created_item
    assert created_item["name"] == menu_item_data["name"]
    assert created_item["price"] == menu_item_data["price"]


def test_update_menu_item(client: TestClient, test_db):
    login_data = {
        "username": "piy",
        "password": "123"
    }
    access_token = utils.create_access_token(data={"sub": login_data["username"], "role": "admin"})
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    updated_data = {
        "name": "Updated Pizza",
        "description": "Updated Cheese Pizza",
        "price": 15
    }
    update_response = client.put(f"/menu/1/", json=updated_data, headers=headers)

    assert update_response.status_code == 200
    updated_item = update_response.json()

    assert updated_item["name"] == updated_data["name"]
    assert updated_item["description"] == updated_data["description"]
    assert updated_item["price"] == updated_data["price"]

    