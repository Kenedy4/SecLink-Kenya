from faker import Faker #type: ignore
from models import db, Student, Teacher, Class, Subject, Parent, Notification
from app import app

fake = Faker()

def seed_database():
    with app.app_context():
        # Add Teachers
        for _ in range(5):
            teacher = Teacher(name=fake.name(), email=fake.email())
            teacher.password = fake.password()
            db.session.add(teacher)

        db.session.commit()

        # Add Classes
        for _ in range(4):
            teacher = Teacher.query.order_by(db.func.random()).first()
            class_obj = Class(class_name=fake.word(), teacher_id=teacher.id)
            db.session.add(class_obj)

        db.session.commit()

        # Add Students
        for _ in range(20):
            class_obj = Class.query.order_by(db.func.random()).first()
            student = Student(
                name=fake.name(),
                dob=fake.date_of_birth(),
                class_id=class_obj.id,
                teacher_id=class_obj.teacher_id,
                email=fake.email(),
            )
            student.password = fake.password()
            db.session.add(student)

        db.session.commit()

        # Add Subjects
        for _ in range(5):
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
