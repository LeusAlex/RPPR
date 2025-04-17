#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Убедитесь, что nest_asyncio установлен
get_ipython().system('pip install nest_asyncio')

import nest_asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

# Применяем nest_asyncio, чтобы разрешить использование asyncio в Jupyter
nest_asyncio.apply()

app = FastAPI()

# Эндпоинт для корневого пути
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Calculator!"}

# Модели для входных данных
class Expression(BaseModel):
    a: float
    b: float
    op: str

class ComplexExpression(BaseModel):
    expression: str

# Функция для выполнения базовых операций
def calculate(a: float, b: float, op: str) -> float:
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        if b == 0:
            raise HTTPException(status_code=400, detail="Division by zero is not allowed.")
        return a / b
    else:
        raise HTTPException(status_code=400, detail="Invalid operator.")

# Эндпоинт для базовых операций
@app.post("/calculate")
async def basic_calculation(expression: Expression):
    result = calculate(expression.a, expression.b, expression.op)
    return {"result": result}

# Эндпоинт для сложных выражений
@app.post("/evaluate")
async def evaluate_expression(complex_expression: ComplexExpression):
    expression = complex_expression.expression

    # Проверка на допустимые символы
    if not re.match(r'^[\d\+\-\*\/\(\)\s]+$', expression):
        raise HTTPException(status_code=400, detail="Invalid characters in expression.")
    
    try:
        # Вычисление выражения
        result = eval(expression)
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"result": result}

# Запуск приложения
if __name__ == "__main__":
    # Запускаем сервер в Jupyter
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


# In[ ]:




