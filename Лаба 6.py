#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install psycopg2-binary')


# In[3]:


import nest_asyncio
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import csv
import os
import redis
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uvicorn

# Примените nest_asyncio для поддержки асинхронного кода в Jupyter
nest_asyncio.apply()

# Настройка базы данных
DATABASE_URL = "postgresql://username:password@localhost/dbname?client_encoding=UTF8"  # Измените на свои данные
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String, index=True)
    name = Column(String)
    faculty = Column(String)
    course = Column(String)
    grade = Column(Float)

Base.metadata.create_all(bind=engine)

app = FastAPI()
cache = redis.Redis(host='localhost', port=6379, db=0)

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Модель для загрузки студентов
class StudentCreate(BaseModel):
    id: int
    surname: str
    name: str
    faculty: str
    course: str
    grade: float

# Эндпоинт для загрузки данных из CSV
@app.post("/students/load/")
def load_students(file_path: str, background_tasks: BackgroundTasks):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File not found")
    
    background_tasks.add_task(load_students_from_csv, file_path)
    return {"message": "Loading students from CSV file in the background"}

def load_students_from_csv(file_path: str):
    db = SessionLocal()
    with open(file_path, mode='r', encoding='utf-8') as file:  # Указываем кодировку
        reader = csv.DictReader(file)
        for row in reader:
            student = Student(
                id=int(row['id']),
                surname=row['surname'],
                name=row['name'],
                faculty=row['faculty'],
                course=row['course'],
                grade=float(row['grade'])
            )
            db.add(student)
        db.commit()
    db.close()

# Эндпоинт для удаления студентов по ID
@app.delete("/students/delete/")
def delete_students(ids: List[int], background_tasks: BackgroundTasks):
    background_tasks.add_task(delete_students_from_db, ids)
    return {"message": "Deleting students in the background"}

def delete_students_from_db(ids: List[int]):
    db = SessionLocal()
    db.query(Student).filter(Student.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    db.close()

# Эндпоинт для получения студентов с кешированием
@app.get("/students/", response_model=List[StudentCreate])
def read_students(db: Session = Depends(get_db)):
    cached_students = cache.get("students")
    if cached_students:
        return cached_students  # Возвращаем кешированные данные

    students = db.query(Student).all()
    cache.set("students", students)  # Кешируем данные
    return students

# Запуск приложения
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# In[ ]:




