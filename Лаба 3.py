#!/usr/bin/env python
# coding: utf-8

# In[4]:


from sqlalchemy import create_engine, Column, String, Integer, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import csv

# Определение модели данных
Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    surname = Column(String, nullable=False)
    name = Column(String, nullable=False)
    faculty = Column(String, nullable=False)
    course = Column(String, nullable=False)  
    grade = Column(Float, nullable=False)

# Создание базы данных
engine = create_engine('sqlite:///students.db') 
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class StudentDatabase:
    def __init__(self):
        self.session = Session()

    def insert_student(self, surname, name, faculty, course, grade):
        new_student = Student(surname=surname, name=name, faculty=faculty, course=course, grade=grade)
        self.session.add(new_student)
        self.session.commit()

    def load_students_from_csv(self, csv_file):
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    self.insert_student(
                        surname=row['Фамилия'],
                        name=row['Имя'],
                        faculty=row['Факультет'],
                        course=row['Курс'],  
                        grade=float(row['Оценка'])
                    )
                except ValueError as e:
                    print(f"Ошибка при добавлении студента {row['Имя']} {row['Фамилия']}: {e}")

    def get_students_by_faculty(self, faculty_name):
        return self.session.query(Student).filter(Student.faculty == faculty_name).all()

    def get_unique_courses(self):
        return self.session.query(Student.course).distinct().all()

    def get_average_grade_by_faculty(self, faculty_name):
        return self.session.query(func.avg(Student.grade)).filter(Student.faculty == faculty_name).scalar()

# Пример использования
if __name__ == '__main__':
    db = StudentDatabase()
    
    # Заполнение базы данных из CSV
    db.load_students_from_csv('students.csv')
    
    # Получение списка студентов по факультету
    students = db.get_students_by_faculty('АВТФ') 
    for student in students:
        print(student.surname, student.name)
    
    # Получение уникальных курсов
    unique_courses = db.get_unique_courses()
    print("Уникальные дисциплины:", unique_courses)
    
    # Получение среднего балла по факультету
    average_grade = db.get_average_grade_by_faculty('ФЛА') 
    print("Средний балл по факультету:", average_grade)


# In[ ]:




