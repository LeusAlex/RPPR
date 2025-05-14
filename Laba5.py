#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Установка необходимых библиотек
get_ipython().system('pip install fastapi uvicorn nest_asyncio python-multipart')

# Импорт необходимых модулей
import nest_asyncio
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn

# Применение nest_asyncio
nest_asyncio.apply()

# Создание экземпляра FastAPI
app = FastAPI()

# Инициализация базовой аутентификации
security = HTTPBasic()

# Определение модели данных
class Student(BaseModel):
    id: int
    surname: str
    name: str
    faculty: str
    course: str
    grade: float

class User(BaseModel):
    username: str
    password: str

# Пример данных
students = []
users = {}

# Эндпоинты API для студентов
@app.post("/students/", response_model=Student)
def create_student(student: Student, credentials: HTTPBasicCredentials = Depends(security)):
    if not authenticate(credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    students.append(student)
    return student

@app.get("/students/", response_model=List[Student])
def read_students(credentials: HTTPBasicCredentials = Depends(security)):
    if not authenticate(credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return students

@app.get("/students/{student_id}", response_model=Student)
def read_student(student_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    if not authenticate(credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    for student in students:
        if student.id == student_id:
            return student
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: Student, credentials: HTTPBasicCredentials = Depends(security)):
    if not authenticate(credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    for index, existing_student in enumerate(students):
        if existing_student.id == student_id:
            students[index] = student
            return student
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

@app.delete("/students/{student_id}")
def delete_student(student_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    if not authenticate(credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    for index, existing_student in enumerate(students):
        if existing_student.id == student_id:
            del students[index]
            return {"message": "Student deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

# Эндпоинты API для аутентификации
@app.post("/auth/register/")
def register(user: User):
    if user.username in users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User  already registered")
    users[user.username] = user.password
    return {"message": "User  registered successfully"}

@app.post("/auth/login/")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username not in users or users[credentials.username] != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "User  logged in successfully"}

@app.post("/auth/logout/")
def logout(credentials: HTTPBasicCredentials = Depends(security)):
    # Для базовой аутентификации нет состояния сессии, но можно вернуть сообщение
    if credentials.username in users:
        return {"message": "User  logged out successfully"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# Функция аутентификации
def authenticate(credentials: HTTPBasicCredentials):
    return credentials.username in users and users[credentials.username] == credentials.password

# Запуск сервера
uvicorn.run(app, host="127.0.0.1", port=8000)


# In[ ]:




