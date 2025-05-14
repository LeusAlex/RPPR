#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Установка необходимых библиотек
get_ipython().system('pip install fastapi uvicorn nest_asyncio')

# Импорт необходимых модулей
import nest_asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn

# Применение nest_asyncio
nest_asyncio.apply()

# Создание экземпляра FastAPI
app = FastAPI()

# Определение модели данных
class Student(BaseModel):
    id: int
    surname: str
    name: str
    faculty: str
    course: str
    grade: float

# Пример данных
students = []

# Эндпоинты API
@app.post("/students/", response_model=Student)
def create_student(student: Student):
    students.append(student)
    return student

@app.get("/students/", response_model=List[Student])
def read_students():
    return students

@app.get("/students/{student_id}", response_model=Student)
def read_student(student_id: int):
    for student in students:
        if student.id == student_id:
            return student
    return {"error": "Student not found"}

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: Student):
    for index, existing_student in enumerate(students):
        if existing_student.id == student_id:
            students[index] = student
            return student
    return {"error": "Student not found"}

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for index, existing_student in enumerate(students):
        if existing_student.id == student_id:
            del students[index]
            return {"message": "Student deleted"}
    return {"error": "Student not found"}

# Запуск сервера
uvicorn.run(app, host="127.0.0.1", port=8000)


# In[ ]:




