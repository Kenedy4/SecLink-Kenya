import os
from functools import wraps
from flask import Flask, jsonify, request, session, send_from_directory
from flask_restful import Api, Resource
from models import Grade, db, Student, Teacher, Parent, Class, Subject, Notifications, LearningMaterial, PasswordResetToken
from flask_mail import Mail
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask_migrate import Migrate 
from flask_bcrypt import Bcrypt 
from flask_jwt_extended import JWTManager, create_access_token 
import datetime
import secrets
from flask_mail import Message
from flask_cors import CORS


# Flask app setup
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'SECRET_KEY'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///seclinkkenya.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['UPLOAD_FOLDER'] = 'uploads'  
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}  
app.config['PORT'] = 5555  

# Initializing necessary extensions
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)
CORS(app)
api = Api(app)

# Initializing the database
db.init_app(app)

# Ensure the 'uploads' folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Helper function to check if a user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'parent_id' not in session:
            return jsonify({"error": "Unauthorized access, please log in"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith("Bearer "):
            return jsonify({'message': 'Token is missing or in incorrect format!'}), 403
        
        try:
            token = token.split()[1]  # Extract token part
            decoded_token = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = Teacher.query.get(decoded_token['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 404
        except Exception as e:
            return jsonify({'message': f'Error processing token: {str(e)}'}), 400

        return f(current_user, *args, **kwargs)
    
    return decorated

# Error handler for internal server errors
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error", "message": str(e)}), 500

######  Routes Using RESTful API ######

## Home Route #####
class Welcome(Resource):
    def get(self):
        return {"message": "Welcome to SecLink Kenya"}, 200

# Auth Routes
class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        if role == 'teacher':
            new_user = Teacher(username=username, email=data.get('email'))
        elif role == 'parent':
            new_user = Parent(username=username, email=data.get('email'))
        else:
            return {"message": 'Invalid role.'}, 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user.password = hashed_password

        db.session.add(new_user)
        db.session.commit()

        return {"message": f'{role.capitalize()} registered successfully.'}, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = Teacher.query.filter_by(username=username).first()

        if not user:
            user = Parent.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = 'teacher' if isinstance(user, Teacher) else 'parent'


            token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=1))

            return {
                'id': user.id,
                'username': user.username,
                'role': session['role'],
                'token': token
            }, 200
        
        return {"error": 'Invalid credentials'}, 401

class CheckSession(Resource):
    @login_required
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": 'No active session'}, 401
        
        # Try to fetch the user first from the Teacher table, then from the Parent table
        user = Teacher.query.get(user_id)
        if not user:
            user = Parent.query.get(user_id)
        
        if not user:
            return {"error": 'User not found'}, 404
        
        # Identify the role based on the instance type
        role = 'teacher' if isinstance(user, Teacher) else 'parent'
        
        # Return the user's data along with their role
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': role
        }, 200


class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        session.pop('role', None)
        return {}, 204

## Teacher Route #
class Teacher(Resource):
    @login_required
    @token_required
    def get(self, teacher_id=None):
        teacher_id = session.get('user_id')
        teacher = Teacher.query.get_or_404(teacher_id)

        # Get all students in the teacher's class
        students = Student.query.filter_by(teacher_id=teacher.id).all()
        parents = Parent.query.join(Student).filter(Student.teacher_id == teacher.id).all()

        return {
            'students': [student.to_dict() for student in students],
            'parents': [parent.to_dict() for parent in parents]
        }, 200

    @login_required
    @token_required
    def post(self):
        data = request.get_json()
        teacher = Teacher.query.get_or_404(session.get('user_id'))

        if 'learning_material' in data:
            # Upload learning material
            learning_material = LearningMaterial(
                title=data.get('title'),
                file_path=data.get('file_path'),
                teacher_id=teacher.id,
                student_id=data.get('student_id')
            )
            db.session.add(learning_material)
            db.session.commit()
            return learning_material.to_dict(), 201

        if 'grade' in data:
            # Post or update student grades
            student_id = data.get('student_id')
            grade = Grade.query.filter_by(student_id=student_id).first()

            if grade:
                # Update grade
                grade.grade = data.get('grade')
            else:
                # Post new grade
                new_grade = Grade(
                    grade=data.get('grade'),
                    student_id=student_id,
                    subject_id=data.get('subject_id')
                )
                db.session.add(new_grade)
            db.session.commit()
            return {"message": "Grade updated successfully"}, 200

        if 'notification' in data:
            # Post new notification to a single or all parents
            parent_id = data.get('parent_id')
            if parent_id:
                notification = Notifications(
                    message=data.get('message'),
                    parent_id=parent_id
                )
            else:
                # Notify all parents of students in the class
                parents = Parent.query.join(Student).filter(Student.teacher_id == teacher.id).all()
                for parent in parents:
                    notification = Notifications(
                        message=data.get('message'),
                        parent_id=parent.id
                    )
                    db.session.add(notification)
            db.session.commit()
            return {"message": "Notification sent successfully"}, 201

    @login_required
    @token_required
    def put(self, learning_material_id):
        # Update learning material
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)
        data = request.get_json()

        learning_material.title = data.get('title', learning_material.title)
        learning_material.file_path = data.get('file_path', learning_material.file_path)

        db.session.commit()
        return learning_material.to_dict(), 200

    @login_required
    @token_required
    def delete(self, learning_material_id):
        # Remove/Delete learning material
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)
        db.session.delete(learning_material)
        db.session.commit()
        return {"message": "Learning material deleted successfully"}, 204

## Parent Route ##
class Parent(Resource):
    @login_required
    @token_required
    def get(self, parent_id=None):
        parent_id = session.get('user_id')
        parent = Parent.query.get_or_404(parent_id)

        # View all the details of their students
        students = Student.query.filter_by(parent_id=parent.id).all()
        notifications = Notifications.query.filter_by(parent_id=parent.id).all()
        learning_materials = LearningMaterial.query.join(Student).filter(Student.parent_id == parent.id).all()

        return {
            'students': [student.to_dict() for student in students],
            'notifications': [notification.to_dict() for notification in notifications],
            'learning_materials': [learning_material.to_dict() for learning_material in learning_materials]
        }, 200

    @login_required
    @token_required
    def get_notifications(self):
        parent_id = session.get('user_id')
        parent = Parent.query.get_or_404(parent_id)
        notifications = Notifications.query.filter_by(parent_id=parent.id).all()
        return jsonify([notification.to_dict() for notification in notifications]), 200

    @login_required
    @token_required
    def get_learning_material(self, learning_material_id):
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)
        return jsonify(learning_material.to_dict()), 200

    @login_required
    @token_required
    def download_learning_material(self, learning_material_id):
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)
        file_path = learning_material.file_path
        file_name = os.path.basename(file_path)

        try:
            return send_from_directory(app.config['UPLOAD_FOLDER'], file_name, as_attachment=True)
        except FileNotFoundError:
            return {"error": "File not found"}, 404
        
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
    @token_required
    def post(self):
        data = request.get_json()
        notification = Notifications(
            message=data.get('message'),
            parent_id=data.get('parent_id')
        )
        db.session.add(notification)
        db.session.commit()
        return notification.to_dict(), 201

    @login_required
    @token_required
    def delete(self, notification_id):
        notification = Notifications.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
        return {"message": "Notification deleted successfully"}, 204

class LearningMaterial(Resource):
    @login_required
    @token_required
    def get(self, learning_material_id=None):
        if learning_material_id:
            # Fetch a single learning material by ID
            learning_material = LearningMaterial.query.get_or_404(learning_material_id)
            return learning_material.to_dict(), 200
        
        # Fetch all learning materials
        learning_materials = LearningMaterial.query.all()
        return jsonify([lm.to_dict() for lm in learning_materials]), 200

    @login_required
    @token_required
    def delete(self, learning_material_id):
        # Delete a learning material by ID
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)
        db.session.delete(learning_material)
        db.session.commit()
        return {"message": "Learning material deleted successfully"}, 204


class LearningMaterialUpload(Resource):
    @login_required
    @token_required
    def post(self):
        # Ensure the request contains a file
        if 'file' not in request.files:
            return {"error": "No file part"}, 400

        file = request.files['file']
        if file.filename == '':
            return {"error": "No selected file"}, 400

        # Ensure the file has a valid extension
        if file and allowed_file(file.filename):
            # Secure the filename and save it
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Save the learning material to the database
            data = request.form  # This retrieves any additional form data
            teacher_id = session.get('user_id')  # Get teacher ID from the session
            learning_material = LearningMaterial(
                title=data.get('title'),
                file_path=file_path,
                teacher_id=teacher_id,
                subject_id=data.get('subject_id')
            )

            db.session.add(learning_material)
            db.session.commit()

            return {"message": "File uploaded successfully", "learning_material": learning_material.to_dict()}, 201
        else:
            return {"error": "Invalid file format. Allowed formats: pdf, docx, txt"}, 400
class LearningMaterialDownload(Resource):
    @login_required
    @token_required
    def get(self, learning_material_id):
        # Fetch the learning material from the database
        learning_material = LearningMaterial.query.get_or_404(learning_material_id)

        # Retrieve the file path from the database record
        file_path = learning_material.file_path
        file_name = os.path.basename(file_path)

        try:
            # Send the file for download
            return send_from_directory(app.config['UPLOAD_FOLDER'], file_name, as_attachment=True)
        except FileNotFoundError:
            return {"error": "File not found"}, 404


class RequestPasswordReset(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')

        # First try to find the user in the Teacher table, then in the Parent table
        user = Teacher.query.filter_by(email=email).first()
        if not user:
            user = Parent.query.filter_by(email=email).first()

        if not user:
            return {"message": 'User not found'}, 404

        # Generate a secure random token and set expiry
        token = secrets.token_urlsafe(20)  # A secure random token
        expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token valid for 1 hour

        # Save the token in the database
        reset_token = PasswordResetToken(user_id=user.id, token=token, expiry_date=expiry)
        db.session.add(reset_token)
        db.session.commit()

        # Create and send the reset link via email
        reset_link = f"{app.config['FRONTEND_URL']}/reset-password?token={token}"
        msg = Message('Password Reset Request', recipients=[email])
        msg.body = f"Use the following link to reset your password: {reset_link}"
        mail.send(msg)

        return {"message": 'Password reset link sent to your email.'}, 200
class PasswordResetConfirm(Resource):
    def post(self):
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')

        # Look up the reset token
        reset_token = PasswordResetToken.query.filter_by(token=token).first()

        if not reset_token:
            return {"message": 'Invalid or expired token'}, 400

        # Check if the token has expired
        if reset_token.expiry_date < datetime.datetime.utcnow():
            return {"message": 'Token has expired'}, 400

        # Try to find the user in the Teacher and Parent tables using the reset token
        user = Teacher.query.get(reset_token.user_id)
        if not user:
            user = Parent.query.get(reset_token.user_id)

        if not user:
            return {"message": 'User not found'}, 404

        # Update the user's password
        user.password = generate_password_hash(new_password)
        db.session.commit()

        # Delete the used reset token
        db.session.delete(reset_token)
        db.session.commit()

        return {"message": 'Password has been updated successfully.'}, 200


# Adding resources (endpoints)
api.add_resource(Welcome, '/')  # Home route
api.add_resource(Signup, '/signup')  # Signup route
api.add_resource(Login, '/login')  # Login route
api.add_resource(CheckSession, '/check-session')  # Check session route
api.add_resource(Logout, '/logout')  # Logout route

# Teacher-related routes
api.add_resource(Teacher, '/teachers', '/teachers/<int:teacher_id>')  # Access teacher details, students, parents, etc.

# Parent-related routes
api.add_resource(Parent, '/parents', '/parents/<int:parent_id>')  # Access parent details, notifications, learning materials

# Notification routes
api.add_resource(Notifications, '/notifications', '/notifications/<int:notification_id>')  # Access notifications

# Learning material routes
api.add_resource(LearningMaterial, '/learning-materials', '/learning-materials/<int:learning_material_id>')  # Access learning materials
api.add_resource(LearningMaterialUpload, '/upload')  # Upload learning material
api.add_resource(LearningMaterialDownload, '/download/<int:learning_material_id>')  # Download learning material

# Password reset routes
api.add_resource(RequestPasswordReset, '/password-reset-request')  # Password reset request
api.add_resource(PasswordResetConfirm, '/password-reset-confirm')  # Password reset confirmation


# app execution point
if __name__ == '__main__':
    app.run(port=5555, debug=True)
