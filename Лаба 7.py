#!/usr/bin/env python
# coding: utf-8

# In[4]:


pip install pytest


# In[2]:


from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import csv
import os
import redis

# Настройка SQLAlchemy
DATABASE_URL = "postgresql://myuser:mypassword@localhost/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Определение модели данных
class StudentDB(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String)
    name = Column(String)
    faculty = Column(String)
    course = Column(String)
    grade = Column(Float)

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Настройка FastAPI
app = FastAPI()
security = HTTPBasic()

# Модели данных
class User(BaseModel):
    username: str
    password: str

users = {}

# Функция аутентификации
def authenticate(credentials: HTTPBasicCredentials):
    return credentials.username in users and users[credentials.username] == credentials.password

@app.post("/auth/register/")
def register(user: User):
    if user.username in users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User  already registered")
    users[user.username] = user.password
    return {"message": "User  registered successfully"}

@app.post("/auth/login/")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    if not authenticate(credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "User  logged in successfully"}

@app.post("/auth/logout/")
def logout(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username in users:
        return {"message": "User  logged out successfully"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


# In[3]:


import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Тесты для эндпоинта регистрации
def test_register_success():
    response = client.post("/auth/register/", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json() == {"message": "User  registered successfully"}

def test_register_duplicate_user():
    client.post("/auth/register/", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/register/", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 400
    assert response.json() == {"detail": "User  already registered"}

# Тесты для эндпоинта логина
def test_login_success():
    client.post("/auth/register/", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/login/", auth=("testuser", "testpass"))
    assert response.status_code == 200
    assert response.json() == {"message": "User  logged in successfully"}

def test_login_invalid_credentials():
    response = client.post("/auth/login/", auth=("testuser", "wrongpass"))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

# Тесты для эндпоинта логаута
def test_logout_success():
    client.post("/auth/register/", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/logout/", auth=("testuser", "testpass"))
    assert response.status_code == 200
    assert response.json() == {"message": "User  logged out successfully"}

def test_logout_without_login():
    response = client.post("/auth/logout/", auth=("nonexistentuser", "testpass"))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
    
# Тесты для эндпоинта создания студента
def test_create_student_success():
    client.post("/auth/register/", json={"username": "testuser", "password": "testpass"})
    client.post("/auth/login/", auth=("testuser", "testpass"))
    
    response = client.post("/students/", json={
        "id": 1,
        "surname": "Doe",
        "name": "John",
        "faculty": "Computer Science",
        "course": "1",
        "grade": 4.5
    }, auth=("testuser", "testpass"))
    
    assert response.status_code == 200
    assert response.json()["surname"] == "Doe"

def test_create_student_unauthorized():
    response = client.post("/students/", json={
        "id": 2,
        "surname": "Smith",
        "name": "Jane",
        "faculty": "Mathematics",
        "course": "2",
        "grade": 3.8
    })
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

# Тесты для эндпоинта получения списка студентов
def test_get_students_success():
    client.post("/auth/register/", json={"username": "testuser", "password": "testpass"})
    client.post("/auth/login/", auth=("testuser", "testpass"))
    
    client.post("/students/", json={
        "id": 3,
        "surname": "Brown",
        "name": "Alice",
        "faculty": "Physics",
        "course": "3",
        "grade": 4.0
    }, auth=("testuser", "testpass"))
    
    response = client.get("/students/", auth=("testuser", "testpass"))
    
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_students_unauthorized():
    response = client.get("/students/")
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    


# In[5]:


pytest test_main.py


# In[ ]:




