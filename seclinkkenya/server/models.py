from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import validates

db = SQLAlchemy()

# Association tables
student_subject = db.Table('student_subject',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'))
)

parent_notification = db.Table('parent_notification',
    db.Column('parent_id', db.Integer, db.ForeignKey('parent.id')),
    db.Column('notification_id', db.Integer, db.ForeignKey('notification.id'))
)

student_notification = db.Table('student_notification',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('notification_id', db.Integer, db.ForeignKey('notification.id'))
)

# Models

class Student(db.Model, SerializerMixin):
    __tablename__ = 'student'
    
    serialize_only = ('id', 'name', 'dob', 'class_id', 'teacher_id')
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    
    subjects = db.relationship('Subject', secondary=student_subject, backref='students')

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


class Teacher(db.Model, SerializerMixin):
    __tablename__ = 'teacher'
    
    serialize_only = ('id', 'name', 'email')
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    
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


class Parent(db.Model, SerializerMixin):
    __tablename__ = 'parent'
    
    serialize_only = ('id', 'name', 'email')
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    
    notifications = db.relationship('Notification', secondary=parent_notification, backref='parents')
    children = db.relationship('Student', backref='parent')

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


class Class(db.Model, SerializerMixin):
    __tablename__ = 'class'
    
    serialize_only = ('id', 'class_name', 'teacher_id')
    
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    
    subjects = db.relationship('Subject', backref='class')


class Subject(db.Model, SerializerMixin):
    __tablename__ = 'subject'
    
    serialize_only = ('id', 'subject_name', 'subject_code', 'class_id', 'teacher_id')
    
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(10), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)


class Notification(db.Model, SerializerMixin):
    __tablename__ = 'notification'
    
    serialize_only = ('id', 'message', 'timestamp')
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    students = db.relationship('Student', secondary=student_notification, backref='notifications')


class LearningMaterial(db.Model, SerializerMixin):
    __tablename__ = 'learning_material'
    
    serialize_only = ('id', 'title', 'file_path', 'upload_date', 'teacher_id', 'subject_id')
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)


class PasswordResetToken(db.Model, SerializerMixin):
    __tablename__ = 'password_reset_token'
    
    serialize_only = ('id', 'user_id', 'token', 'expiry_date')
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)