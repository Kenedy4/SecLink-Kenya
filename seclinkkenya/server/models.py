from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import validates

db = SQLAlchemy()

# Association table for students and subjects (including student_name and class_id)
student_subject = db.Table('student_subject',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
    db.Column('student_name', db.String(100), nullable=False),
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'))
)

# Base class for common user functionality
class BaseUser(db.Model, SerializerMixin):
    __abstract__ = True
    name = db.Column(db.String(100), nullable=False)  # Inherited by Teacher, Parent, and Student
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @hybrid_property
    def password(self):
        return self._password_hash

    @password.setter
    def password(self, plaintext_password):
        if plaintext_password:
            self._password_hash = generate_password_hash(plaintext_password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address, "Invalid email format"
        return address

class Teacher(BaseUser):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50))
    
    # Relationships
    classes = db.relationship('Class', backref='teacher')
    learning_materials = db.relationship('LearningMaterial', backref='uploader')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,  # Inherited from BaseUser
            'username': self.username,
            'email': self.email,
            'subject': self.subject,
            'classes': [c.to_dict() for c in self.classes],
            'learning_materials': [lm.to_dict() for lm in self.learning_materials]
        }

class Parent(BaseUser):
    __tablename__ = 'parents'
    id = db.Column(db.Integer, primary_key=True)
    
    # Relationships
    children = db.relationship('Student', back_populates='parent', foreign_keys='Student.parent_id')
    notifications = db.relationship('Notifications', back_populates='parent', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,  # Inherited from BaseUser
            'username': self.username,
            'email': self.email,
            'children': [child.to_dict() for child in self.children],
            'notifications': [notification.to_dict() for notification in self.notifications]
        }

class Student(BaseUser):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    dob = db.Column(db.Date, nullable=False)
    overall_grade = db.Column(db.String(2), nullable=True)

    # Foreign keys and relationships
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)

    parent = db.relationship('Parent', back_populates='children', foreign_keys=[parent_id])
    grades = db.relationship('Grade', backref='student', lazy=True, cascade="all, delete-orphan")
    subjects = db.relationship('Subject', secondary=student_subject, backref='students')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,  # Inherited from BaseUser
            'dob': self.dob.isoformat(),
            'class_id': self.class_id,
            'teacher_id': self.teacher_id,
            'parent_id': self.parent_id,
            'overall_grade': self.overall_grade,
            'grades': [grade.to_dict() for grade in self.grades],
            'subjects': [subject.to_dict() for subject in self.subjects]
        }

    def calculate_overall_grade(self):
        if not self.grades:
            return None

        total_score = sum(self._convert_letter_to_points(grade.grade) for grade in self.grades)
        average_score = total_score / len(self.grades)

        self.overall_grade = self._convert_points_to_letter(average_score)
        db.session.commit()

    @staticmethod
    def _convert_letter_to_points(letter):
        return {'A': 4, 'B': 3, 'C': 2, 'D': 1}.get(letter, 0)

    @staticmethod
    def _convert_points_to_letter(points):
        if points >= 85:
            return 'A'
        elif points >= 75:
            return 'B'
        elif points >= 65:
            return 'C'
        elif points >= 55:
            return 'D'
        return 'E'

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
            'subjects': [subject.to_dict() for subject in self.subjects]
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
    token = db.Column(db.String(100), nullable=False, unique=True)
    expiry_date = db.Column(db.DateTime, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)

    parent = db.relationship('Parent', backref='password_reset_tokens')
    teacher = db.relationship('Teacher', backref='password_reset_tokens')
    student = db.relationship('Student', backref='password_reset_tokens')

    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'expiry_date': self.expiry_date.isoformat(),
            'parent_id': self.parent_id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id
        }
        