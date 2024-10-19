from faker import Faker  # type: ignore
from models import db, Student, Teacher, Class, Subject, Parent, Notifications
from app import app
from werkzeug.security import generate_password_hash

fake = Faker()

def seed_database():
    with app.app_context():
        # Ensure tables are created
        db.create_all()

        # Add Teachers
        for _ in range(5):
            teacher = Teacher(username=fake.user_name(), email=fake.email())
            teacher.password_hash = generate_password_hash(fake.password())
            db.session.add(teacher)

        db.session.commit()

        # Add Classes
        for _ in range(5):
            teacher = Teacher.query.order_by(db.func.random()).first()  # Get a random teacher
            class_obj = Class(class_name=fake.word(), teacher_id=teacher.id)
            db.session.add(class_obj)

        db.session.commit()

        # Add Parents
        for _ in range(5):
            parent = Parent(username=fake.user_name(), email=fake.email())
            parent.password_hash = generate_password_hash(fake.password())
            db.session.add(parent)

        db.session.commit()

        # Add Students
        for _ in range(20):
            class_obj = Class.query.order_by(db.func.random()).first()
            parent = Parent.query.order_by(db.func.random()).first()
            student = Student(
                name=fake.name(),  # Correctly assign name
                username=fake.user_name(),  # Assign username if required
                dob=fake.date_of_birth(),
                class_id=class_obj.id,
                teacher_id=class_obj.teacher_id,
                parent_id=parent.id,
                email=fake.email(),
            )
            
            student.password_hash = generate_password_hash(fake.password())
            db.session.add(student)

        # Add Subjects
        for _ in range (5):
            class_obj = Class.query.order_by(db.func.random()).first()
            subject = Subject(
                subject_name=fake.word(),
                subject_code=fake.random_number(digits=5),
                class_id=class_obj.id,
                teacher_id=class_obj.teacher_id
            )
            db.session.add(subject)

        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
