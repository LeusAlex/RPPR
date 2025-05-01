#!/usr/bin/env python
# coding: utf-8

# In[2]:


pip install fastapi uvicorn nest_asyncio


# In[2]:


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import date
import re

app = FastAPI()

# Модель для валидации данных абонента
class Subscriber(BaseModel):
    surname: str
    name: str
    birth_date: date
    phone_number: str
    email: EmailStr

    @classmethod
    def validate_surname(cls, surname: str):
        if not re.match(r'^[А-ЯЁ][а-яё]+$', surname):
            raise ValueError("Фамилия должна начинаться с заглавной буквы и содержать только кириллицу.")
        return surname

    @classmethod
    def validate_name(cls, name: str):
        if not re.match(r'^[А-ЯЁ][а-яё]+$', name):
            raise ValueError("Имя должно начинаться с заглавной буквы и содержать только кириллицу.")
        return name

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_surname
        yield cls.validate_name

# Эндпойнт для сбора обращений абонентов
@app.post("/subscribers/")
async def create_subscriber(subscriber: Subscriber):
    return {"message": "Обращение успешно зарегистрировано!", "subscriber": subscriber}

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)


# In[ ]:




