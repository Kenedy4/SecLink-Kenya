from flask import Flask
from models import db, Teacher, Parent, Student, Class, Subject, Grade, Notifications, LearningMaterial
from flask_bcrypt import Bcrypt
from datetime import datetime, date, timezone  # Import timezone for UTC datetime
from config import Config  # Import your app's config

# Initialize Flask app and configuration
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)

def seed_data():
    # Ensure all operations happen within the app context
    with app.app_context():
        # Drop all existing tables and recreate them (be cautious in production environments)
        db.drop_all()  # Warning: This will delete all data in the database
        db.create_all()

        # Create sample data for Teachers
        teacher_1 = Teacher(
            name="Fredrick Kariuki",
            username="kariukifred",
            email="fredrichkkariuki@gmail.com",
            password="password123",
            subject="Mathematics"
        )

        teacher_2 = Teacher(
            name="Jane Katiwa",
            username="katiwasm",
            email="katiwasmith@gmail.com",
            password="password123",
            subject="Science"
        )

        # Create sample data for Parents
        parent_1 = Parent(
            name="Michael Angels",
            username="mjohnson",
            email="mangels@gmail.com",
            password="password123"
        )

        parent_2 = Parent(
            name="Sarah Achieng",
            username="Sarachieng",
            email="sachieng@gmail.com",
            password="password123"
        )

        # Create sample data for Students (using `date` for dob and `datetime` for created_at)
        student_1 = Student(
            name="Augustine Musyoki",
            dob=date(2010, 5, 14),  # Convert dob to `date` object
            class_id=1,
            teacher_id=1,
            parent_id=1,
            overall_grade="A",
            created_at=datetime.now(timezone.utc)  # Set the current time for created_at with timezone
        )

        student_2 = Student(
            name="Filcitity Ndanu",
            dob=date(2009, 8, 22),  # Convert dob to `date` object
            class_id=2,
            teacher_id=2,
            parent_id=2,
            overall_grade="B",
            created_at=datetime.now(timezone.utc)  # Set the current time for created_at with timezone
        )

        # Create sample data for Classes
        class_1 = Class(
            class_name="Math Class",
            teacher_id=1
        )

        class_2 = Class(
            class_name="Science Class",
            teacher_id=2
        )

        # Create sample data for Subjects
        subject_1 = Subject(
            subject_name="Algebra",
            subject_code="MATH101",
            class_id=1,
            teacher_id=1
        )

        subject_2 = Subject(
            subject_name="Physics",
            subject_code="SCI101",
            class_id=2,
            teacher_id=2
        )

        # Create sample data for Grades
        grade_1 = Grade(
            grade="A",
            student_id=1,
            subject_id=1
        )

        grade_2 = Grade(
            grade="B",
            student_id=2,
            subject_id=2
        )

        # Create sample data for Learning Materials
        learning_material_1 = LearningMaterial(
            title="Algebra Basics",
            file_path="/materials/algebra_basics.pdf",
            teacher_id=1,
            student_id=1
        )

        learning_material_2 = LearningMaterial(
            title="Physics 101",
            file_path="/materials/physics_101.pdf",
            teacher_id=2,
            student_id=2
        )

        # Create sample data for Notifications
        notification_1 = Notifications(
            message="Parent-teacher meeting scheduled for next week.",
            parent_id=1
        )

        notification_2 = Notifications(
            message="School fees deadline approaching.",
            parent_id=2
        )

        # Add everything to the session and commit
        db.session.add_all([
            teacher_1, teacher_2, 
            parent_1, parent_2, 
            student_1, student_2, 
            class_1, class_2, 
            subject_1, subject_2, 
            grade_1, grade_2, 
            learning_material_1, learning_material_2,
            notification_1, notification_2
        ])
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
