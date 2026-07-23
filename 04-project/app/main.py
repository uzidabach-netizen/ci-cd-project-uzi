from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI(title="Student Portal")

DATA_FILE = "students.json"


def load_students() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_students(students: list):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=2)


class Student(BaseModel):
    name: str
    email: str
    grade: str


@app.get("/")
def root():
    return {"message": "Welcome to Student Portal"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/students")
def get_students():
    return load_students()


@app.get("/students/{student_id}")
def get_student(student_id: int):
    students = load_students()
    for s in students:
        if s["id"] == student_id:
            return s
    raise HTTPException(status_code=404, detail="Student not found")


@app.post("/students", status_code=201)
def create_student(student: Student):
    students = load_students()
    new_id = max((s["id"] for s in students), default=0) + 1
    new_student = {"id": new_id, **student.model_dump()}
    students.append(new_student)
    save_students(students)
    return new_student


@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    students = load_students()
    for i, s in enumerate(students):
        if s["id"] == student_id:
            students[i] = {"id": student_id, **student.model_dump()}
            save_students(students)
            return students[i]
    raise HTTPException(status_code=404, detail="Student not found")


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    students = load_students()
    for i, s in enumerate(students):
        if s["id"] == student_id:
            deleted = students.pop(i)
            save_students(students)
            return {"message": "Student deleted", "student": deleted}
    raise HTTPException(status_code=404, detail="Student not found")
