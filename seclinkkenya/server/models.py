from flask_sqlalchemy import SQLAlchemy #type: ignore
from sqlalchemy.ext.hybrid import hybrid_property #type: ignore
from sqlalchemy_serializer import SerializerMixin  #type: ignore
from werkzeug.security import generate_password_hash, check_password_hash  #type: ignore
from datetime import datetime

from sqlalchemy.orm import validates # type: ignore

db = SQLAlchemy()

# Association tables
# Association tables
student_subject = db.Table('student_subject',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'))
)

# Models
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    serialize_only = ('id', 'username', 'email')
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Teacher(User):
    __tablename__ = 'teachers'
    
    user = db.relationship('User', backref='teacher', uselist=False)
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    subject = db.Column(db.String(50))
    
    classes = db.relationship('Class', backref='teacher')
    learning_materials = db.relationship('LearningMaterial', backref='uploader')

    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, plaintext_password):
        self._password_hash = generate_password_hash(plaintext_password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address, "Invalid email format"
        return address


class Parent(User):
    __tablename__ = 'parents'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship('User', backref='parent_profile', uselist=False)

    # Relationship to children (Students)
    children = db.relationship('Student', back_populates='parent', foreign_keys='Student.parent_id')
            # Relationship to notification 
    notifications = db.relationship('Notifications', back_populates='parent', cascade="all, delete-orphan")


    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, plaintext_password):
        self._password_hash = generate_password_hash(plaintext_password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address, "Invalid email format"
        return address


class Student(User, SerializerMixin):
    __tablename__ = 'students'
    
    serialize_only = ('id', 'name', 'dob', 'class_id', 'teacher_id', 'parent_id', 'overall_grade')
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)
    # email = db.Column(db.String(100), unique=True, nullable=False)
    # _password_hash = db.Column(db.String(128), nullable=False)
    
    overall_grade = db.Column(db.String(2), nullable=True)  # Store overall grade (A, B, C, D, or E)

    # Relationship to Parent
    parent = db.relationship('Parent', back_populates='children', foreign_keys=[parent_id])

    # Grades relationship
    grades = db.relationship('Grade', backref='student', lazy=True)  # Link to Grade

    subjects = db.relationship('Subject', secondary=student_subject, backref='students')

 # Method to calculate the overall grade based on subject grades
    def calculate_overall_grade(self):
        if not self.grades:
            return None  # No grades available

        total_score = 0
        for grade in self.grades:
            total_score += self._convert_letter_to_points(grade.grade)

        # Calculate the average score
        average_score = total_score / len(self.grades)

        # Convert the average score back to a letter grade
        self.overall_grade = self._convert_points_to_letter(average_score)
        db.session.commit()

    # Helper method to convert letter grades to points (A = 4, B = 3, etc.)
    def _convert_letter_to_points(self, letter):
        if letter == 'A':
            return 4
        elif letter == 'B':
            return 3
        elif letter == 'C':
            return 2
        elif letter == 'D':
            return 1
        else:
            return 0  # For 'E'

    # Helper method to convert points to a letter grade
    def _convert_points_to_letter(self, points):
        if points >= 85:
            return 'A'
        elif points >= 75:
            return 'B'
        elif points >= 65:
            return 'C'
        elif points >= 55:
            return 'D'
        else:
            return 'E'

class Grade(db.Model, SerializerMixin):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(2), nullable=False)  # Store grade like A, B, C, D, E
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    subject = db.relationship('Subject', backref='grades')


class Class(db.Model, SerializerMixin):
    __tablename__ = 'classes'
    
    serialize_only = ('id', 'class_name', 'teacher_id')
    
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    
    subjects = db.relationship('Subject', backref='class')


class Subject(db.Model, SerializerMixin):
    __tablename__ = 'subjects'
    
    serialize_only = ('id', 'subject_name', 'subject_code', 'class_id', 'teacher_id')
    
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(10), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)


class Notifications(db.Model, SerializerMixin):
    __tablename__ = 'notifications'
    
    serialize_only = ('id', 'message', 'created_at', 'updated_at')
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    # students = db.relationship('Student', secondary=student_notification, backref='notifications')
        # Foreign key to Parent
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)

    # Relationship to Parent
    parent = db.relationship('Parent', back_populates='notifications')


class LearningMaterial(db.Model, SerializerMixin):
    __tablename__ = 'learning_material'
    
    serialize_only = ('id', 'title', 'file_path', 'upload_date', 'teacher_id', 'subject_id')
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)



class PasswordResetToken(db.Model, SerializerMixin):
    __tablename__ = 'password_reset_tokens'  # Renamed for consistency
    
    serialize_only = ('id', 'user_id', 'token', 'expiry_date')
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    expiry_date = db.Column(db.DateTime, nullable=False)
    
    # Relationship to User (optional)
    user = db.relationship('User', backref='password_reset_tokens')
