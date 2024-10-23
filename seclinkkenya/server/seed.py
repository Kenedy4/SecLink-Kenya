from flask import Flask
from models import db, Teacher, Parent, Student, Class, Subject, Grade, Notifications, LearningMaterial
from flask_bcrypt import Bcrypt
from datetime import datetime
from config import Config  # Import your app's config

# Initialize Flask app and configuration
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)

# Seed data function
def seed_data():
    with app.app_context():
        # Drop all existing tables and recreate them (be cautious in production environments)
        db.drop_all()  # Warning: This will delete all data in the database
        db.create_all()

        # Create teachers
        teacher1 = Teacher(
            name="Alice Johnson",
            username="alicej",
            email="alice@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'),
            subject="Math"
        )

        teacher2 = Teacher(
            name="Bob Smith",
            username="bobsmith",
            email="bob@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'),
            subject="Science"
        )

        # Create parents
        parent1 = Parent(
            name="John Doe",
            username="johndoe",
            email="john@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode('utf-8')
        )

        parent2 = Parent(
            name="Jane Roe",
            username="janeroe",
            email="jane@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode('utf-8')
        )

        # Add the teachers and parents to the session and commit to generate IDs
        db.session.add_all([teacher1, teacher2, parent1, parent2])
        db.session.commit()  # Commit to generate the IDs for teachers and parents

        # Create classes
        class1 = Class(class_name="Math 101", teacher_id=teacher1.id)
        class2 = Class(class_name="Science 101", teacher_id=teacher2.id)

        # Add classes to the session and commit to generate IDs
        db.session.add_all([class1, class2])
        db.session.commit()

        # Create subjects and commit them to ensure subject_id is available
        subject1 = Subject(subject_name="Algebra", subject_code="MTH101", class_id=class1.id, teacher_id=teacher1.id)
        subject2 = Subject(subject_name="Physics", subject_code="SCI101", class_id=class2.id, teacher_id=teacher2.id)

        db.session.add_all([subject1, subject2])
        db.session.commit()  # Commit subjects to generate IDs

        # Create students with the correct teacher_id
        student1 = Student(
            name="Sam Doe",
            username="samdoe",
            email="sam@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'),
            dob=datetime.strptime("2008-05-12", "%Y-%m-%d").date(),
            class_id=class1.id,
            teacher_id=teacher1.id,  # Assign teacher1 as the teacher
            parent_id=parent1.id
        )
        student2 = Student(
            name="Emily Roe",
            username="emilyroe",
            email="emily@example.com",
            password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'),
            dob=datetime.strptime("2009-06-22", "%Y-%m-%d").date(),
            class_id=class2.id,
            teacher_id=teacher2.id,  # Assign teacher2 as the teacher
            parent_id=parent2.id
        )

        # Add students to the session and commit to generate IDs
        db.session.add_all([student1, student2])
        db.session.commit()

        # Create grades with valid subject_id
        grade1 = Grade(grade="A", student_id=student1.id, subject_id=subject1.id)  # Ensure subject1.id is set
        grade2 = Grade(grade="B", student_id=student2.id, subject_id=subject2.id)  # Ensure subject2.id is set

        # Create notifications
        notification1 = Notifications(message="Parent-teacher meeting", parent_id=parent1.id)
        notification2 = Notifications(message="Field trip permission", parent_id=parent2.id)

        # Create learning materials with valid student_id
        learning_material1 = LearningMaterial(
            title="Algebra Basics",
            file_path="/path/to/algebra.pdf",
            teacher_id=teacher1.id,
            student_id=student1.id  # Ensure student1's ID is set here
        )
        learning_material2 = LearningMaterial(
            title="Physics Principles",
            file_path="/path/to/physics.pdf",
            teacher_id=teacher2.id,
            student_id=student2.id  # Ensure student2's ID is set here
        )

        # Add all remaining objects to session
        db.session.add_all([grade1, grade2, notification1, notification2, learning_material1, learning_material2])

        # Commit the session to write to the database
        db.session.commit()

        print("Database seeded successfully!")

# Run seed function
if __name__ == '__main__':
    seed_data()
