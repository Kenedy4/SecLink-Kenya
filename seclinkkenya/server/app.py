import os
from functools import wraps
from flask import Flask, config, jsonify, request, session, send_from_directory
from flask_restful import Api, Resource
from .models import db, User, Student, Teacher, Parent, Class, Subject, Notifications, LearningMaterial, PasswordResetToken
from .config import Config
from flask_mail import Mail
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask_migrate import Migrate # type: ignore
from flask_bcrypt import Bcrypt # type: ignore
from flask_jwt_extended import JWTManager # type: ignore
import datetime
import secrets
from flask_mail import Message
# from auth import CheckSession, Login, Logout, Signup
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)

# Initializing necessary extensions extensions
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)
CORS = (app)
api = Api(app)


# Initializing the database
db.init_app(app)

# File upload configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Adds file upload configuration inside the app context
with app.app_context():
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Ensures the 'uploads' folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper function to check allowed file extensions
def allowed_file(filename):
    allowed_extensions = app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
# Helper function to check if a user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'parent_id' not in session:
            return jsonify({"error": "Unauthorized access, please log"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token or not token.startswith("Bearer "):
            return jsonify({'message': 'Token is missing or incorrect format!'}), 403
        
        try:
            # Extract token part from 'Bearer <token>'
            token = token.split()[1]
            decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(decoded_token['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        except Exception as e:
            return jsonify({'message': f'Error processing token: {str(e)}'}), 400
        
        return f(current_user, *args, **kwargs)
    
    return decorated




######  Routes Using RESTful API ######

                ## Home Route #####
class Welcome(Resource):
    def get(self):
        return jsonify({"message": "Welcome to SecLink"}), 200
    
                ##  Auth Route  ######
class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        if role == 'teacher':
            new_user = Teacher(username=username)
        elif role == 'parent':
            new_user = Parent(username=username)
        else:
            return jsonify({'message': 'Invalid role.'}), 400

        # Hash the password before storing
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user.password = hashed_password

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': f'{role.capitalize()} registered successfully.'}), 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role  # Store user role in session

            # Generate a JWT token for authentication
            token = jwt.encode(
                {"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                app.config['SECRET_KEY'],
                algorithm="HS256"
            )

            return jsonify({
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'token': token
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401

class CheckSession(Resource):
    @login_required
    def get(self):
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if user:
            return {'id': user.id, 'username': user.username, 'role': user.role}, 200  # Include role in response
        return jsonify({'error': 'User not found'}), 404
    
class Logout(Resource):
    def delete(self):
        if session.get('user_id') is None:
            return jsonify({'error': 'Unauthorized'}), 401  # Return 401 when no active session
        session.pop('user_id', None)
        session.pop('role', None)  # Remove the role from session
        return {}, 204


                ##  User Route  ######
                
class User(Resource):
    @token_required
    def get(self, user_id=None):
        if user_id:
            # Fetch specific user by ID
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify(user.to_dict()), 200
        else:
            # Fetch all users
            users = User.query.all()
            return jsonify([user.to_dict() for user in users]), 200

    @token_required
    def post(self):
        data = request.get_json()
        role = data.get('role')
        username = data.get('username')
        password = data.get('password')
        
        if role == 'teacher':
            new_user = Teacher(username=username)
        elif role == 'parent':
            new_user = Parent(username=username)
        else:
            return jsonify({'message': 'Invalid role.'}), 400

        # Hash the password before storing
        new_user.password = data.get('password')
        
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': f'{role.capitalize()} registered successfully.'}), 201

    @token_required
    def get(self, role):
        if role == 'parent':
            users = Parent.query.all()
        elif role == 'teacher':
            users = Teacher.query.all()
        else:
            return jsonify({'error': 'Invalid role provided'}), 400

        return jsonify([user.to_dict() for user in users]), 200

                ## Parent Route ##
class Parent(Resource):
    @token_required
    def get(self, parent_id=None):
        if parent_id:
            # Fetch a specific parent
            parent = Parent.query.get_or_404(parent_id)
            return jsonify(parent.to_dict())
        else:
            # Fetch all parents (optional)
            parents = Parent.query.all()
            return jsonify([parent.to_dict() for parent in parents])

class Notifications(Resource):
    @token_required
    def get(self):
        parent_id = session.get('parent_id')
        parent = Parent.query.get_or_404(parent_id)
        notifications = Notifications.query.filter_by(parent_id=parent.id).all()
        return jsonify([notification.to_dict() for notification in notifications]), 200

class Student(Resource):
    @token_required
    def get(self):
        parent_id = session.get('parent_id')
        parent = Parent.query.get_or_404(parent_id)
        students = Student.query.filter_by(parent_id=parent.id).all()
        return jsonify([student.to_dict() for student in students]), 200

                ## Teacher Route ##
class Teacher(Resource):
    @login_required
    @token_required
    def get(self, teacher_id=None):
        if teacher_id:
            teacher = Teacher.query.get_or_404(teacher_id)
            return jsonify(teacher.to_dict()), 200
        teachers = Teacher.query.all()
        return jsonify([teacher.to_dict() for teacher in teachers]), 200

    @login_required
    @token_required
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
    @token_required
    def put(self, teacher_id):
        data = request.get_json()
        teacher = Teacher.query.get_or_404(teacher_id)
        teacher.name = data.get('name')
        teacher.email = data.get('email')
        db.session.commit()
        return jsonify(teacher.to_dict()), 200

    @login_required
    @token_required
    def delete(self, teacher_id):
        teacher = Teacher.query.get_or_404(teacher_id)
        db.session.delete(teacher)
        db.session.commit()
        return '', 204
                ##  Student Route ##
class Student (Resource):
     def get(self, student_id=None):
        if student_id:
            # Get a single student by ID
            student = Student.query.get(student_id)
            if not student:
                return jsonify({'message': 'Student not found'}), 404
            return jsonify(student.to_dict())  
        else:
            # Get all students
            students = Student.query.all()
            return jsonify([student.to_dict() for student in students])  

                ##  LearningMaterial Route ##
class LearningMaterial(Resource):
    @login_required
    @token_required
    def get(self, learning_material_id=None):
        if learning_material_id:
            learning_material = LearningMaterial.query.get_or_404(learning_material_id)
            return learning_material.to_dict(), 200
        learning_materials = LearningMaterial.query.all()
        return jsonify([learning_material.to_dict() for learning_material in learning_materials]), 200

    @login_required
    def delete(self, learning_material_id):
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)
        db.session.delete(learning_material)
        db.session.commit()
        return '', 204
                ##  LearningMaterialUpload Route ##
class LearningMaterialUpload(Resource):
    @login_required
    @token_required
    def post(self):
        # Ensures the user is a teacher
        user_id = session.get('user_id')
        teacher = Teacher.query.get(user_id)

        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

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
                ##  LearningMaterialDownload Route ##
class LearningMaterialDownload(Resource):
    @login_required
    @token_required
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
            return jsonify({"error": "File not found"}), 404
        
                ##  Dashboard Route ##
class Dashboard(Resource):
    @token_required
    def get(self):
        parent_id = session.get('parent_id')
        parent = Parent.query.get_or_404(parent_id)
        notifications = Notifications.query.filter_by(parent_id=parent.id).all()
        students = Student.query.filter_by(parent_id=parent.id).all()
        learning_materials = LearningMaterial.query.filter_by(parent_id=parent.id).all()
        return {
            'notifications': [notification.to_dict() for notification in notifications],
           'students': [student.to_dict() for student in students],
            'learning_materials': [learning_material.to_dict() for learning_material in learning_materials]
        }, 200
        
                ##  Notification Route ##
class Notifications(Resource):
    @login_required
    @token_required
    def get(self, notification_id=None):
        if notification_id:
            notification = Notifications.query.get_or_404(notification_id)
            return notification.to_dict(), 200
        notifications = Notifications.query.all()
        return jsonify([notification.to_dict() for notification in notifications]), 200

    @login_required
    def post(self):
        data = request.get_json()
        notification = Notifications(
            message=data.get('message'),
        )
        db.session.add(notification)
        db.session.commit()
        return notification.to_dict(), 201

    @login_required
    def delete(self, notification_id):
        notification = Notifications.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
        return '', 204

                ##  Class Route ##
class Class(Resource):
    @token_required 
    @login_required
    def get(self, class_id=None):
        if class_id:
            # Fetch the class by class_id
            class_obj = Class.query.get(class_id)
            if not class_obj:
                return jsonify({'message': 'Class not found.'}), 404
            return jsonify(class_obj.to_dict()), 200
        else:
            # Fetch all classes if no class_id is provided
            classes = Class.query.all()
            return jsonify([class_obj.to_dict() for class_obj in classes]), 200
                ##  Subject Route ##
class Subject(Resource):
    @login_required
    @token_required
    def get(self, subject_id=None):
        if subject_id:
            subject = Subject.query.get_or_404(subject_id)
            return subject.to_dict(), 200
        subjects = Subject.query.all()
        return jsonify([subject.to_dict() for subject in subjects]), 200

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

            ## PasswordResetting Route ##

class RequestPasswordReset(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')

        # Check if the user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Generate a unique reset token
        token = secrets.token_urlsafe(20)  # A secure random token
        expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token valid for 1 hour

        # Save the token in the database
        reset_token = PasswordResetToken(user_id=user.id, token=token, expiry_date=expiry)
        db.session.add(reset_token)
        db.session.commit()

        # Send reset token via email
        reset_link = f"{app.config['FRONTEND_URL']}/reset-password?token={token}"
        msg = Message('Password Reset Request', recipients=[email])
        msg.body = f"Use the following link to reset your password: {reset_link}"
        email.send(msg)

        return jsonify({'message': 'Password reset link sent to your email.'}), 200


class PasswordResetConfirm(Resource):
    def post(self):
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')

        # Find the token in the database
        reset_token = PasswordResetToken.query.filter_by(token=token).first()

        if not reset_token:
            return jsonify({'message': 'Invalid or expired token'}), 400

        # Check if the token is expired
        if reset_token.expiry_date < datetime.datetime.utcnow():
            return jsonify({'message': 'Token has expired'}), 400

        # Update the user's password
        user = User.query.get(reset_token.user_id)
        user.password = generate_password_hash(new_password)
        db.session.commit()

        # Delete the token after use
        db.session.delete(reset_token)
        db.session.commit()

        return jsonify({'message': 'Password has been updated successfully.'}), 200


# Adding resources (endpoints)
api.add_resource(Welcome, '/', '/welcome')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check-session')
api.add_resource(Logout, '/logout')

    # Password reset endpoints
api.add_resource(RequestPasswordReset, '/password-reset-request') 
api.add_resource(PasswordResetConfirm, '/password-reset-confirm')

    # Other resources
api.add_resource(User, '/users', '/users/<int:user_id>')
api.add_resource(Parent, '/parents', '/parents/<int:parent_id>')
api.add_resource(Student, '/students', '/students/<int:student_id>')
api.add_resource(Teacher, '/teachers', '/teachers/<int:teacher_id>')
api.add_resource(Class, '/classes', '/classes/<int:class_id>')
api.add_resource(Subject, '/subjects', '/subjects/<int:subject_id>')
api.add_resource(Notifications, '/notifications', '/notifications/<int:notification_id>')
api.add_resource(LearningMaterial, '/learning_materials', '/learning_materials/<int:learning_material_id>')
api.add_resource(LearningMaterialUpload, '/upload')
api.add_resource(LearningMaterialDownload, '/download/<int:learning_material_id>')
api.add_resource(Dashboard, '/dashboard')

# app execution point
if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True)
