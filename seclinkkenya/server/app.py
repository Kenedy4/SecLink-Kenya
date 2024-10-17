import os
from flask import Flask, request, session, jsonify, send_from_directory # type: ignore
# from flask_sqlalchemy import SQLAlchemy # type: ignore
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
# Initialize SQLAlchemy

# Initialize extensions
# db = SQLAlchemy()
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)


db.init_app(app)
# Directory for saving uploaded files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Directory for saving uploaded files
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

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
        # username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        

        if not email or not password :
            return jsonify({'error': 'email and password are required.'}), 422

        # user = Teacher(email=email)
        hash_password = bcrypt.generate_password_hash(password)  # Using hybrid property for password hashing
        # user.password =  hash_password  # Using hybrid property for password hashing
        user = User(email=email, password=hash_password)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'User already exists.'}, 422

        session['user_id'] = user.id
        return jsonify({'id': user.id, 'email': user.email}), 201 #'username': user.name,

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return {'id': user.id, 'email': user.email}, 200 #'username': user.name,

        return jsonify({'error': 'Invalid credentials'}), 401

class CheckSession(Resource):
    @login_required
    def get(self):
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if user:
            return {'id': user.id,  'email': user.email}, 200 #'username': user.name,
        return jsonify({'error': 'User not found'}), 404

# ======================== STUDENT ROUTES =========================

class Student(Resource):
    # @login_required
    def get(self, student_id=None):
        if student_id:
            student = Student.query.get_or_404(student_id)
            return student.to_dict(), 200
        students = Student.query.all()
        return jsonify([student.to_dict() for student in students]), 200

    # @login_required
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

    # @login_required
    def put(self, student_id):
        data = request.get_json()
        student = Student.query.get_or_404(student_id)
        student.name = data.get('name')
        student.dob = data.get('dob')
        student.class_id = data.get('class_id')
        student.teacher_id = data.get('teacher_id')
        db.session.commit()
        return student.to_dict(), 200

    # @login_required
    def patch(self, student_id):
        data = request.get_json()
        student = Student.query.get_or_404(student_id)
        if 'name' in data:
            student.name = data.get('name')
        if 'dob' in data:
            student.dob = data.get('dob')
        db.session.commit()
        return student.to_dict(), 200

    # @login_required
    def delete(self, student_id):
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return '', 204

# ======================== TEACHER ROUTES =========================

class Teacher(Resource):
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

# ======================== CLASS ROUTES =========================

class Class(Resource):
    @login_required
    def get(self, class_id=None):
        if class_id:
            class_obj = Class.query.get_or_404(class_id)
            return class_obj.to_dict(), 200
        classes = Class.query.all()
        return [class_obj.to_dict() for class_obj in classes], 200

    @login_required
    def post(self):
        data = request.get_json()
        class_obj = Class(
            class_name=data.get('class_name'),
            teacher_id=data.get('teacher_id'),
        )
        db.session.add(class_obj)
        db.session.commit()
        return class_obj.to_dict(), 201

    @login_required
    def put(self, class_id):
        data = request.get_json()
        class_obj = Class.query.get_or_404(class_id)
        class_obj.class_name = data.get('class_name')
        db.session.commit()
        return class_obj.to_dict(), 200

    @login_required
    def delete(self, class_id):
        class_obj = Class.query.get_or_404(class_id)
        db.session.delete(class_obj)
        db.session.commit()
        return '', 204

# ======================== SUBJECT ROUTES =========================

class Subject(Resource):
    @login_required
    def get(self, subject_id=None):
        if subject_id:
            subject = Subject.query.get_or_404(subject_id)
            return subject.to_dict(), 200
        subjects = Subject.query.all()
        return [subject.to_dict() for subject in subjects], 200

    @login_required
    def post(self):
        data = request.get_json()
        subject = Subject(
            subject_name=data.get('subject_name'),
            subject_code=data.get('subject_code'),
            class_id=data.get('class_id'),
            teacher_id=data.get('teacher_id'),
        )
        db.session.add(subject)
        db.session.commit()
        return subject.to_dict(), 201

    @login_required
    def put(self, subject_id):
        data = request.get_json()
        subject = Subject.query.get_or_404(subject_id)
        subject.subject_name = data.get('subject_name')
        subject.subject_code = data.get('subject_code')
        db.session.commit()
        return subject.to_dict(), 200

    @login_required
    def delete(self, subject_id):
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        return '', 204

# ======================== NOTIFICATION ROUTES =========================

class Notification(Resource):
    @login_required
    def get(self, notification_id=None):
        if notification_id:
            notification = Notification.query.get_or_404(notification_id)
            return notification.to_dict(), 200
        notifications = Notification.query.all()
        return [notification.to_dict() for notification in notifications], 200

    @login_required
    def post(self):
        data = request.get_json()
        notification = Notification(
            message=data.get('message'),
        )
        db.session.add(notification)
        db.session.commit()
        return notification.to_dict(), 201

    @login_required
    def delete(self, notification_id):
        notification = Notification.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
        return '', 204

# ======================== LEARNING MATERIAL ROUTES =========================

class LearningMaterial(Resource):
    @login_required
    def get(self, learning_material_id=None):
        if learning_material_id:
            learning_material = LearningMaterial.query.get_or_404(learning_material_id)
            return learning_material.to_dict(), 200
        learning_materials = LearningMaterial.query.all()
        return [learning_material.to_dict() for learning_material in learning_materials], 200

    @login_required
    def delete(self, learning_material_id):
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)
        db.session.delete(learning_material)
        db.session.commit()
        return '', 204

# Route for uploading learning material (POST with file)
class LearningMaterialUpload(Resource):
    @login_required
    def post(self):
        # Ensure the user is a teacher
        user_id = session.get('user_id')
        teacher = Teacher.query.get(user_id)

        if 'file' not in request.files:
            return {"error": "No file part"}, 400

        file = request.files['file']

        if file.filename == '':
            return {"error": "No selected file"}, 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Save the file path and related information in the database
            data = request.form  # Get additional form data
            learning_material = LearningMaterial(
                title=data.get('title'),
                file_path=filename,
                teacher_id=teacher.id,
                subject_id=data.get('subject_id')  # Assuming subject is provided
            )

            db.session.add(learning_material)
            db.session.commit()

            return {"message": "File uploaded successfully"}, 201

        return {"error": "Invalid file format"}, 400

# Route for downloading learning material (GET to download file)
class LearningMaterialDownload(Resource):
    @login_required
    def get(self, learning_material_id):
        # Fetch the learning material by ID
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)

        # Extract the file path stored in the database
        file_path = learning_material.file_path
        file_name = os.path.basename(file_path)

        # Send the file to the user for download
        try:
            return send_from_directory(app.config['UPLOAD_FOLDER'], file_name, as_attachment=True)
        except FileNotFoundError:
            return {"error": "File not found"}, 404

# ======================== ROUTE REGISTRATION =========================
api.add_resource(Welcome, '/', '/welcome')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check-session')

api.add_resource(Student, '/students', '/students/<int:student_id>')
api.add_resource(Teacher, '/teachers', '/teachers/<int:teacher_id>')
api.add_resource(Class, '/classes', '/classes/<int:class_id>')
api.add_resource(Subject, '/subjects', '/subjects/<int:subject_id>')
api.add_resource(Notification, '/notifications', '/notifications/<int:notification_id>')
api.add_resource(LearningMaterial, '/learning_materials', '/learning_materials/<int:learning_material_id>')
api.add_resource(LearningMaterialUpload, '/upload')
api.add_resource(LearningMaterialDownload, '/download/<int:learning_material_id>')

if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True) 