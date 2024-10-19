from flask_sqlalchemy import SQLAlchemy #type: ignore
from sqlalchemy.ext.hybrid import hybrid_property #type: ignore
from sqlalchemy_serializer import SerializerMixin  #type: ignore
from werkzeug.security import generate_password_hash, check_password_hash  #type: ignore
from datetime import datetime

from sqlalchemy.orm import validates # type: ignore

db = SQLAlchemy()

# Association tables
student_subject = db.Table('student_subject',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'))
)

# Models
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()  
        }

class Teacher(User):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    subject = db.Column(db.String(50))
    
    classes = db.relationship('Class', backref='teacher')
    learning_materials = db.relationship('LearningMaterial', backref='uploader')

    def to_dict(self):
        return {
            **super().to_dict(),  # Include parent class data (from User)
            'subject': self.subject,
            'classes': [c.to_dict() for c in self.classes],  # Serialize related objects
            'learning_materials': [lm.to_dict() for lm in self.learning_materials]
        }

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
    
    children = db.relationship('Student', back_populates='parent', foreign_keys='Student.parent_id')
    notifications = db.relationship('Notifications', back_populates='parent', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            **super().to_dict(),  # Include parent class data (from User)
            'children': [child.to_dict() for child in self.children],
            'notifications': [notification.to_dict() for notification in self.notifications]
        }


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
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)
    overall_grade = db.Column(db.String(2), nullable=True)

    parent = db.relationship('Parent', back_populates='children', foreign_keys=[parent_id])
    grades = db.relationship('Grade', backref='student', lazy=True)
    subjects = db.relationship('Subject', secondary=student_subject, backref='students')

    def to_dict(self):
        return {
            **super().to_dict(),  # Include parent class data (from User)
            'name': self.name,
            'dob': self.dob.isoformat(),  # Serialize date
            'class_id': self.class_id,
            'teacher_id': self.teacher_id,
            'parent_id': self.parent_id,
            'overall_grade': self.overall_grade,
            'grades': [grade.to_dict() for grade in self.grades],  # Serialize relationships
            'subjects': [subject.to_dict() for subject in self.subjects]
        }


class Grade(db.Model, SerializerMixin):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(2), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    subject = db.relationship('Subject', backref='grades')

    def to_dict(self):
        return {
            'id': self.id,
            'grade': self.grade,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'subject': self.subject.subject_name
        }


class Class(db.Model, SerializerMixin):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)

    subjects = db.relationship('Subject', backref='class')

    def to_dict(self):
        return {
            'id': self.id,
            'class_name': self.class_name,
            'teacher_id': self.teacher_id,
            'subjects': [subject.to_dict() for subject in self.subjects]  # Serialize related subjects
        }


class Subject(db.Model, SerializerMixin):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(10), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'subject_name': self.subject_name,
            'subject_code': self.subject_code,
            'class_id': self.class_id,
            'teacher_id': self.teacher_id
        }



class Notifications(db.Model, SerializerMixin):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)

    parent = db.relationship('Parent', back_populates='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'parent_id': self.parent_id
        }

class LearningMaterial(db.Model, SerializerMixin):
    __tablename__ = 'learning_material'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'file_path': self.file_path,
            'upload_date': self.upload_date.isoformat(),
            'teacher_id': self.teacher_id,
            'student_id': self.student_id
        }


class PasswordResetToken(db.Model, SerializerMixin):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    expiry_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref='password_reset_tokens')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'expiry_date': self.expiry_date.isoformat()
        }