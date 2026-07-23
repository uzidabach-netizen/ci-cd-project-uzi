from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import os

app = FastAPI(title="Student Portal v2 - MySQL")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "student_portal"),
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


class Student(BaseModel):
    name: str
    email: str
    grade: str


@app.get("/")
def root():
    return {"message": "Welcome to Student Portal v2 (MySQL)"}


@app.get("/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {str(e)}")


@app.get("/students")
def get_students():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return students


@app.get("/students/{student_id}")
def get_student(student_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.post("/students", status_code=201)
def create_student(student: Student):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO students (name, email, grade) VALUES (%s, %s, %s)",
        (student.name, student.email, student.grade),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM students WHERE id = %s", (new_id,))
    new_student = cursor.fetchone()
    cursor.close()
    conn.close()
    return new_student


@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "UPDATE students SET name=%s, email=%s, grade=%s WHERE id=%s",
        (student.name, student.email, student.grade, student_id),
    )
    conn.commit()
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")
    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    updated = cursor.fetchone()
    cursor.close()
    conn.close()
    return updated


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    if not student:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Student deleted", "student": student}
