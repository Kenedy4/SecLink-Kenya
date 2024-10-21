from flask_bcrypt import Bcrypt, generate_password_hash
from faker import Faker
from models import db, Student, Teacher, Parent, Class, Subject, Notifications, Grade, LearningMaterial
from app import app

# Initialize Faker
fake = Faker()
bcrypt = Bcrypt()
# Seed Teachers
def seed_teachers(num=15):
    teachers = []
    for _ in range(num):
        plaintext_password = fake.password()  # Generate a plaintext password
        hashed_password = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')  # Hash using bcrypt
        teacher = Teacher(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.unique.email(),
            subject=fake.job(),
            password=hashed_password  # Store the bcrypt hashed password
        )
        db.session.add(teacher)  # Add each teacher to the session
        teachers.append(teacher)

    db.session.commit()  # Commit after adding all teachers

    # Print all teachers to ensure they have valid IDs
    for teacher in teachers:
        print(f"Seeded teacher: {teacher.name}, ID: {teacher.id}")  # Check if ID is assigned

    return teachers

# Seed Parents
def seed_parents(num=15):
    parents = []
    for _ in range(num):
        plaintext_password = fake.password()  # Generate a plaintext password
        hashed_password = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')  # Hash using bcrypt
        parent = Parent(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.unique.email(),
            password=hashed_password  # Store the bcrypt hashed password
        )
        db.session.add(parent)  # Add each parent to the session
        parents.append(parent)

    db.session.commit()  # Commit after adding all parents
    return parents

# Seed Classes
def seed_classes(teachers, num=5):
    if not teachers:
        raise ValueError("No teachers available to assign to classes.")

    classes = []
    for _ in range(num):
        teacher = fake.random_element(teachers)
        if not teacher or not teacher.id:
            raise ValueError("Invalid teacher assignment. Make sure teachers have been correctly created.")

        class_obj = Class(
            class_name=fake.word().capitalize(),
            teacher_id=teacher.id  # Ensure a valid teacher_id
        )
        db.session.add(class_obj)  # Add each class to the session
        classes.append(class_obj)

    db.session.commit()  # Commit after adding all classes
    return classes

# Seed Subjects
def seed_subjects(classes, num=5):
    subjects = []
    for _ in range(num):
        class_obj = fake.random_element(classes)
        if class_obj:
            subject = Subject(
                subject_name=fake.word().capitalize(),
                subject_code=str(fake.random_number(digits=5)),
                class_id=class_obj.id,
                teacher_id=class_obj.teacher_id
            )
            db.session.add(subject)  # Add each subject to the session
            subjects.append(subject)

    db.session.commit()  # Commit after adding all subjects
    return subjects

# Seed Students
def seed_students(classes, parents, num=10):
    students = []
    for _ in range(num):
        class_obj = fake.random_element(classes)
        parent = fake.random_element(parents)
        plaintext_password = fake.password()  # Generate a plaintext password
        hashed_password = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')  # Hash using bcrypt
        student = Student(
            name=fake.name(),
            username=fake.user_name(),
            dob=fake.date_of_birth(minimum_age=10, maximum_age=18),
            class_id=class_obj.id,
            teacher_id=class_obj.teacher_id,
            parent_id=parent.id,
            email=fake.unique.email(),
            password=hashed_password  # Store the bcrypt hashed password
        )
        db.session.add(student)  # Add each student to the session
        students.append(student)

    db.session.commit()  # Commit after adding all students
    return students

# Seed Notifications
def seed_notifications(parents, num=10):
    notifications = []
    for _ in range(num):
        parent = fake.random_element(parents)
        notification = Notifications(
            message=fake.sentence(),
            parent_id=parent.id
        )
        db.session.add(notification)  # Add each notification to the session
        notifications.append(notification)

    db.session.commit()  # Commit after adding all notifications

# Seed Grades
def seed_grades(students, subjects, num=20):
    grades = []
    for _ in range(num):
        student = fake.random_element(students)
        subject = fake.random_element(subjects)
        grade = Grade(
            grade=fake.random_element(['A', 'B', 'C', 'D', 'E']),
            student_id=student.id,
            subject_id=subject.id
        )
        db.session.add(grade)  # Add each grade to the session
        grades.append(grade)

    db.session.commit()  # Commit after adding all grades

# Seed Learning Materials
def seed_learning_materials(students, teachers, num=10):
    learning_materials = []
    for _ in range(num):
        student = fake.random_element(students)
        teacher = fake.random_element(teachers)
        learning_material = LearningMaterial(
            title=fake.sentence(),
            file_path=f"uploads/{fake.file_name(extension='pdf')}",
            teacher_id=teacher.id,
            student_id=student.id
        )
        db.session.add(learning_material)  # Add each learning material to the session
        learning_materials.append(learning_material)

    db.session.commit()  # Commit after adding all learning materials

# Function to Seed the Database
def seed_database():
    with app.app_context():
        db.create_all()  # Ensure all tables are created
        
        # Seeding Data
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
