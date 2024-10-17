import os
from flask import Flask, request, session, jsonify, send_from_directory # type: ignore
from flask_restful import Api, Resource # type: ignore
from models import db, Student, Teacher, Class, Subject, Notification, LearningMaterial
from config import Config
from werkzeug.utils import secure_filename # type: ignore
from functools import wraps
from flask_migrate import Migrate #type: ignore
from sqlalchemy.exc import IntegrityError # type: ignore
from flask_bcrypt import Bcrypt # type: ignore

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)

db.init_app(app)

# Directory for saving uploaded files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the 'uploads' folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper function to check if a user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized access, please log in"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'txt'}

# ======================== WELCOME ROUTE =========================

class Welcome(Resource):
    def get(self):
        return jsonify({"message": "Welcome to SecLink"})

# ======================== AUTH ROUTES =========================

class Signup(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'email and password are required.'}), 422

        hash_password = bcrypt.generate_password_hash(password)
        user = Teacher(email=email, password=hash_password)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'User already exists.'}, 422

        session['user_id'] = user.id
        return jsonify({'id': user.id, 'email': user.email}), 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = Teacher.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return {'id': user.id, 'email': user.email}, 200

        return jsonify({'error': 'Invalid credentials'}), 401

class CheckSession(Resource):
    @login_required
    def get(self):
        user_id = session.get('user_id')
        user = Teacher.query.get(user_id)
        if user:
            return {'id': user.id,  'email': user.email}, 200
        return jsonify({'error': 'User not found'}), 404

# ======================== LOGOUT ROUTE =========================

class Logout(Resource):
    def post(self):
        session.clear()
        return jsonify({"message": "Successfully logged out"}), 200

# ======================== STUDENT ROUTES =========================

class StudentResource(Resource):
    def get(self, student_id=None):
        if student_id:
            student = Student.query.get_or_404(student_id)
            return student.to_dict(), 200
        students = Student.query.all()
        return jsonify([student.to_dict() for student in students]), 200

    def post(self):
        data = request.get_json()
        student = Student(
            name=data.get('name'),
            dob=data.get('dob'),
            class_id=data.get('class_id'),
            teacher_id=data.get('teacher_id'),
            email=data.get('email'),
        )
        student.password = data.get('password')

        db.session.add(student)
        db.session.commit()
        return student.to_dict(), 201

    def put(self, student_id):
        data = request.get_json()
        student = Student.query.get_or_404(student_id)
        student.name = data.get('name')
        student.dob = data.get('dob')
        student.class_id = data.get('class_id')
        student.teacher_id = data.get('teacher_id')
        db.session.commit()
        return student.to_dict(), 200

    def patch(self, student_id):
        data = request.get_json()
        student = Student.query.get_or_404(student_id)
        if 'name' in data:
            student.name = data.get('name')
        if 'dob' in data:
            student.dob = data.get('dob')
        db.session.commit()
        return student.to_dict(), 200

    def delete(self, student_id):
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return '', 204

# ======================== TEACHER ROUTES =========================

class TeacherResource(Resource):
    @login_required
    def get(self, teacher_id=None):
        if teacher_id:
            teacher = Teacher.query.get_or_404(teacher_id)
            return jsonify(teacher.to_dict()), 200
        teachers = Teacher.query.all()
        return jsonify([teacher.to_dict() for teacher in teachers]), 200

    @login_required
    def post(self):
        data = request.get_json()
        teacher = Teacher(
            name=data.get('name'),
            email=data.get('email'),
        )
        teacher.password = data.get('password')

        db.session.add(teacher)
        db.session.commit()
        return jsonify(teacher.to_dict()), 201

    @login_required
    def put(self, teacher_id):
        data = request.get_json()
        teacher = Teacher.query.get_or_404(teacher_id)
        teacher.name = data.get('name')
        teacher.email = data.get('email')
        db.session.commit()
        return jsonify(teacher.to_dict()), 200

    @login_required
    def delete(self, teacher_id):
        teacher = Teacher.query.get_or_404(teacher_id)
        db.session.delete(teacher)
        db.session.commit()
        return '', 204

# ======================== ROUTE REGISTRATION =========================

api.add_resource(Welcome, '/', '/welcome')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check-session')
api.add_resource(Logout, '/logout')

api.add_resource(StudentResource, '/students', '/students/<int:student_id>')
api.add_resource(TeacherResource, '/teachers', '/teachers/<int:teacher_id>')

if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True)
