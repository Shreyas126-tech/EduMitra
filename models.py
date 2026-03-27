from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(String(36), primary_key=True, index=True)
    admin_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    password_hash = Column(String(255))

class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, index=True)
    usn = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    password_hash = Column(String(255))
    semester = Column(Integer)
    department = Column(String(50))

    records = relationship("AcademicRecord", back_populates="student", cascade="all, delete-orphan")

class AcademicRecord(Base):
    __tablename__ = "academic_records"

    id = Column(String(36), primary_key=True, index=True)
    student_id = Column(String(36), ForeignKey("students.id"), index=True)
    subject = Column(String(100))
    exam_score = Column(Float)
    assignment_score = Column(Float)
    attendance = Column(Float)
    semester = Column(Integer)

    student = relationship("Student", back_populates="records")
