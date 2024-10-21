from faker import Faker
from models import db, Student, Teacher, Class, Subject, Parent, Notifications, Grade, LearningMaterial
from app import app
from werkzeug.security import generate_password_hash

# Initialize Faker
fake = Faker()

def seed_teachers(num=5):
    teachers = []
    for _ in range(num):
        teacher = Teacher(
            username=fake.user_name(),
            email=fake.email(),
            subject=fake.job()
        )
        teacher.password = generate_password_hash(fake.password())
        teachers.append(teacher)
        db.session.add(teacher)
    db.session.commit()
    return teachers

def seed_parents(num=5):
    parents = []
    for _ in range(num):
        parent = Parent(
            username=fake.user_name(),
            email=fake.email(),
        )
        parent.password = generate_password_hash(fake.password())
        parents.append(parent)
        db.session.add(parent)
    db.session.commit()
    return parents

def seed_classes(teachers, num=5):
    classes = []
    for _ in range(num):
        teacher = fake.random_element(teachers)
        class_obj = Class(
            class_name=fake.word(),
            teacher_id=teacher.id
        )
        classes.append(class_obj)
        db.session.add(class_obj)
    db.session.commit()
    return classes

def seed_subjects(classes, num=5):
    subjects = []
    for _ in range(num):
        class_obj = fake.random_element(classes)
        subject = Subject(
            subject_name=fake.word(),
            subject_code=str(fake.random_number(digits=5)),
            class_id=class_obj.id,
            teacher_id=class_obj.teacher_id
        )
        subjects.append(subject)
        db.session.add(subject)
    db.session.commit()
    return subjects

def seed_students(classes, parents, num=20):
    students = []
    for _ in range(num):
        class_obj = fake.random_element(classes)
        parent = fake.random_element(parents)
        student = Student(
            name=fake.name(),
            username=fake.user_name(),
            dob=fake.date_of_birth(minimum_age=10, maximum_age=18),
            class_id=class_obj.id,
            teacher_id=class_obj.teacher_id,
            parent_id=parent.id,
            email=fake.email(),
        )
        student.password = generate_password_hash(fake.password())
        students.append(student)
        db.session.add(student)
    db.session.commit()
    return students

def seed_notifications(parents, num=10):
    for _ in range(num):
        parent = fake.random_element(parents)
        notification = Notifications(
            message=fake.sentence(),
            parent_id=parent.id
        )
        db.session.add(notification)
    db.session.commit()

def seed_grades(students, subjects, num=20):
    for _ in range(num):
        student = fake.random_element(students)
        subject = fake.random_element(subjects)
        grade = Grade(
            grade=fake.random_element(['A', 'B', 'C', 'D', 'E']),
            student_id=student.id,
            subject_id=subject.id
        )
        db.session.add(grade)
    db.session.commit()

def seed_learning_materials(students, teachers, num=10):
    for _ in range(num):
        student = fake.random_element(students)
        teacher = fake.random_element(teachers)
        learning_material = LearningMaterial(
            title=fake.sentence(),
            file_path=fake.file_path(extension='pdf'),
            teacher_id=teacher.id,
            student_id=student.id
        )
        db.session.add(learning_material)
    db.session.commit()

def seed_database():
    with app.app_context():
        db.create_all()
        
        teachers = seed_teachers()
        parents = seed_parents()
        classes = seed_classes(teachers)
        subjects = seed_subjects(classes)
        students = seed_students(classes, parents)
        
        seed_notifications(parents)
        seed_grades(students, subjects)
        seed_learning_materials(students, teachers)

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
