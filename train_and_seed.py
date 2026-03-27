"""
EduMitra — Train ML Model & Seed Database
Run this script once to set up the application with initial data in PostgreSQL.
"""

import os
import sys
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy.orm import Session

# Ensure we can import from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import models
from database import engine, SessionLocal
from auth import hash_password

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def train_model():
    """Train a Random Forest model and save it locally."""
    print("🧠 Training ML model...")
    np.random.seed(42)
    n = 1000

    exam = np.random.uniform(10, 100, n)
    assign = np.random.uniform(10, 100, n)
    attend = np.random.uniform(20, 100, n)

    # Risk label based on combined score
    combined = exam * 0.4 + assign * 0.2 + attend * 0.4
    labels = []
    for c in combined:
        if c >= 70:
            labels.append("Low Risk")
        elif c >= 45:
            labels.append("Medium Risk")
        else:
            labels.append("High Risk")

    X = np.column_stack([exam, assign, attend])
    y = np.array(labels)

    clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    clf.fit(X, y)

    model_path = os.path.join(DATA_DIR, "model.joblib")
    joblib.dump(clf, model_path)
    print(f"✅ Model saved to {model_path}")
    return clf


def seed_data():
    """Seed sample admins, students, and records into PostgreSQL."""
    print("📋 Seeding sample data into PostgreSQL...")
    
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Force re-seed: Clear existing data to ensure 50 students
        print("🧹 Clearing existing data for a fresh seed...")
        db.query(models.AcademicRecord).delete()
        db.query(models.Student).delete()
        db.query(models.Admin).delete()
        db.commit()

        # ── Create sample admins ────────────────────────────────
        admin_data = [
            {"admin_id": "admin", "name": "Dr. Rajesh Kumar", "email": "admin@edumitra.com", "pw": "admin123"},
            {"admin_id": "admin2", "name": "Prof. Ananya Sharma", "email": "admin2@edumitra.com", "pw": "admin123"},
        ]
        
        for a in admin_data:
            admin = models.Admin(
                id=str(np.random.randint(1000, 9999)),
                admin_id=a["admin_id"],
                name=a["name"],
                email=a["email"],
                password_hash=hash_password(a["pw"])
            )
            db.add(admin)
        print(f"   ✅ {len(admin_data)} admins created")

        # ── Create sample students ──────────────────────────────
        first_names = [
            "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh",
            "Krishna", "Ishaan", "Shaurya", "Ananya", "Diya", "Myra", "Sara",
            "Aadhya", "Ira", "Anika", "Priya", "Kavya", "Riya",
            "Rohan", "Karthik", "Deepak", "Nikhil", "Rahul",
            "Sneha", "Pooja", "Meera", "Lakshmi", "Nandini",
            "Amit", "Suresh", "Vijay", "Ganesh", "Harsha",
            "Divya", "Rashmi", "Swati", "Pallavi", "Tanvi",
            "Akash", "Pranav", "Siddharth", "Varun", "Tarun",
            "Neha", "Shruti", "Bhavana", "Chaitra", "Keerthi"
        ]
        departments = ["CSE", "ISE", "ECE", "ME", "EEE", "CE"]
        semesters = [3, 4, 5, 6]

        students = []
        for i, name in enumerate(first_names):
            dept = departments[i % len(departments)]
            sem = semesters[i % len(semesters)]
            usn = f"1ED22{dept[:2]}{str(i + 1).zfill(3)}"
            student = models.Student(
                id=f"stu{str(i + 1).zfill(3)}",
                usn=usn,
                name=name,
                email=f"{name.lower()}@edumitra.com",
                password_hash=hash_password(usn.lower()),
                semester=sem,
                department=dept
            )
            db.add(student)
            students.append(student)
        
        db.flush() # Ensure student IDs are available for records
        print(f"   ✅ {len(students)} students created")

        # ── Create academic records ─────────────────────────────
        subjects_map = {
            3: ["Data Structures", "Digital Electronics", "Discrete Math", "OOP with Java", "Computer Organization"],
            4: ["Operating Systems", "DBMS", "Computer Networks", "Software Engineering", "Linear Algebra"],
            5: ["Machine Learning", "Web Technologies", "Compiler Design", "Theory of Computation", "Cryptography"],
            6: ["Artificial Intelligence", "Cloud Computing", "Big Data Analytics", "Mobile App Dev", "IoT"],
        }
        
        record_count = 0
        for s in students:
            sem_subjects = subjects_map.get(s.semester, subjects_map[3])
            
            # Performance profiles
            idx = int(s.id.replace("stu", ""))
            if idx % 5 == 0: base = 82 # High
            elif idx % 5 == 1: base = 68 # Good
            elif idx % 5 == 2: base = 55 # Average
            elif idx % 5 == 3: base = 38 # Below average
            else: base = 25 # At risk

            for subj in sem_subjects:
                exam = max(0, min(100, base + np.random.randint(-12, 13)))
                assign = max(0, min(100, base + 5 + np.random.randint(-10, 11)))
                att = max(0, min(100, base + 10 + np.random.randint(-8, 9)))
                
                record = models.AcademicRecord(
                    id=f"rec{str(record_count).zfill(4)}",
                    student_id=s.id,
                    subject=subj,
                    exam_score=float(exam),
                    assignment_score=float(assign),
                    attendance=float(att),
                    semester=s.semester
                )
                db.add(record)
                record_count += 1
        
        db.commit()
        print(f"   ✅ {record_count} academic records created")
        print("\n🎉 PostgreSQL Data seeding complete!")

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    train_model()
    seed_data()
