import os
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory, session
from models import Class, LearningMaterial, Notifications, Student, Subject, db, Teacher, Parent, PasswordResetToken  # Import necessary models
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity
import datetime
import secrets
from flask_mail import Mail, Message
from flask_cors import CORS
from config import Config  # Import the config class

# Flask app setup using Config class
app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from config.py

# Initialize extensions
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)
CORS(app)

# Initialize the database
db.init_app(app)

# Helper function to check allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Error handler for internal server errors
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error", "message": str(e)}), 500


######  Routes ######

@app.route('/')
def welcome():
    return jsonify({"message": "Welcome to SecLink Kenya"}), 200

# Signup Endpoint
# Signup Endpoint
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    # Extract the fields from the request data
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')  # Raw password from request
    email = data.get('email')
    subject = data.get('subject')  # Subject is only used if the user is a teacher
    role = data.get('role')  # Either 'Teacher' or 'Parent'

    # Check if all required fields are provided
    if not (name and username and password and email and role):
        return jsonify({'message': 'All fields are required'}), 400

    # Hash the password using bcrypt
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Handle role-based registration
    if role == 'teacher':
        # Check if the subject is provided for the Teacher role
        if not subject:
            return jsonify({'message': 'Subject is required for Teacher role'}), 400
        
        # Create a new Teacher user
        new_user = Teacher(name=name, username=username, email=email, password_hash=password_hash, subject=subject)

    elif role == 'parent':
        # Create a new Parent user
        new_user = Parent(name=name, username=username, email=email, password_hash=password_hash)

    else:
        return jsonify({'message': 'Invalid role'}), 400

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Return success message
    return jsonify({'message': 'User registered successfully'}), 201


# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Ensure required fields are present
    if not data or not all(key in data for key in ['username', 'password']):
        return jsonify({"error": "Missing required fields"}), 400

    # Query both Teacher and Parent tables for the user
    user = Teacher.query.filter_by(username=data['username']).first() or \
           Parent.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({"error": "User not found"}), 404  # If no user is found

    # Use bcrypt to compare the entered password with the hashed password in the database
    if bcrypt.check_password_hash(user.password_hash, data['password']):
        # If password is correct, generate a JWT token with the role included
        token = create_access_token(identity={"id": user.id, "role": user.__class__.__name__}, expires_delta=datetime.timedelta(hours=3))
        return jsonify({"token": token, "role": user.__class__.__name__}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401  # If password is incorrect

@app.route('/logout', methods=['POST'])
@jwt_required()  # Ensure the user is logged in
def logout():
    # Here we can optionally blacklist the token or just return a success message
    jti = get_jwt()["jti"]  # JWT ID (jti) is unique identifier for the token
    # If token blacklisting is enabled, add the jti to the blacklist (this is optional)
    
    return jsonify({"message": "Logged out successfully"}), 200

# Teacher View all or single students by ID and class
@app.route('/students', methods=['GET'])
@jwt_required()
def view_students():
    identity = get_jwt_identity()
    user = Teacher.query.get(identity['id'])

    if identity['role'] == 'Teacher':
        class_id = request.args.get('class_id')
        if class_id:
            students = Student.query.filter_by(class_id=class_id).all()
        else:
            students = Student.query.all()

        return jsonify([student.to_dict() for student in students]), 200
    else:
        return jsonify({'message': 'Unauthorized'}), 403

# Teacher Upload/Update Learning Materials
@app.route('/learning-material', methods=['POST', 'PUT'])
@jwt_required()
def upload_or_update_learning_material():
    identity = get_jwt_identity()

    # Only Teachers can upload or update learning materials
    if identity['role'] == 'Teacher':
        
        if request.method == 'POST':
            # Handle file upload for new learning material
            if 'file' not in request.files or not request.files['file']:
                return jsonify({'message': 'No file provided'}), 400

            file = request.files['file']
            
            # Validate file type using allowed_file function
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save the file to the specified path
                try:
                    file.save(file_path)
                except Exception as e:
                    return jsonify({'message': f'File could not be saved: {str(e)}'}), 500

                # Create a new LearningMaterial entry in the database
                material = LearningMaterial(
                    title=request.form['title'],  # Title should be in form data
                    file_path=file_path,
                    teacher_id=identity['id']
                )
                db.session.add(material)
                db.session.commit()

                return jsonify({'message': 'Learning material uploaded successfully', 'file_path': file_path}), 200
            else:
                return jsonify({'message': 'Invalid file type'}), 400

        elif request.method == 'PUT':
            # Handle updating an existing learning material
            if 'id' not in request.form:
                return jsonify({'message': 'Material ID is required'}), 400
            
            # Find the material by ID
            material = LearningMaterial.query.get(request.form['id'])
            if not material:
                return jsonify({'message': 'Learning material not found'}), 404

            # Update the title if provided
            if 'title' in request.form:
                material.title = request.form['title']

            # Handle file update if a file is provided
            if 'file' in request.files and allowed_file(request.files['file'].filename):
                file = request.files['file']
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                try:
                    file.save(file_path)
                    material.file_path = file_path
                except Exception as e:
                    return jsonify({'message': f'File could not be saved: {str(e)}'}), 500

            db.session.commit()
            return jsonify({'message': 'Learning material updated successfully'}), 200
    else:
        return jsonify({'message': 'Unauthorized'}), 403


# Teacher Delete Learning Material
@app.route('/learning-material/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_learning_material(id):
    identity = get_jwt_identity()
    if identity['role'] == 'Teacher':
        material = LearningMaterial.query.get(id)
        if material:
            db.session.delete(material)
            db.session.commit()
            return jsonify({'message': 'Material deleted'}), 200
        return jsonify({'message': 'Material not found'}), 404
    return jsonify({'message': 'Unauthorized'}), 403

# Teacher Add Notifications for Parents
@app.route('/notifications', methods=['POST'])
@jwt_required()
def add_notification():
    identity = get_jwt_identity()
    if identity['role'] == 'Teacher':
        data = request.get_json()
        notification = Notifications(
            message=data['message'],
            parent_id=data['parent_id']
        )
        db.session.add(notification)
        db.session.commit()

        return jsonify({'message': 'Notification sent'}), 200
    return jsonify({'message': 'Unauthorized'}), 403



# Parent View their Student Details
@app.route('/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_details(student_id):
    identity = get_jwt_identity()
    if identity['role'] == 'Parent':
        student = Student.query.filter_by(parent_id=identity['id'], id=student_id).first()
        if student:
            return jsonify(student.to_dict()), 200
        return jsonify({'message': 'Student not found'}), 404
    return jsonify({'message': 'Unauthorized'}), 403

# Parent Get Notifications
@app.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    identity = get_jwt_identity()
    if identity['role'] == 'Parent':
        notifications = Notifications.query.filter_by(parent_id=identity['id']).all()
        return jsonify([notif.to_dict() for notif in notifications]), 200
    return jsonify({'message': 'Unauthorized'}), 403

# Parent Download Learning Materials
@app.route('/learning-material', methods=['GET'])
@jwt_required()
def download_learning_material():
    identity = get_jwt_identity()
    if identity['role'] == 'Parent':
        materials = LearningMaterial.query.all()
        return jsonify([material.to_dict() for material in materials]), 200
    return jsonify({'message': 'Unauthorized'}), 403

@app.route('/class', methods=['POST'])
@jwt_required()
def create_class():
    identity = get_jwt_identity()
    if identity['role'] == 'Teacher':  # Or some admin role if applicable
        data = request.get_json()
        class_name = data.get('class_name')
        if not class_name:
            return jsonify({'message': 'Class name is required'}), 400
        
        new_class = Class(class_name=class_name, teacher_id=identity['id'])
        db.session.add(new_class)
        db.session.commit()
        return jsonify({'message': 'Class created successfully', 'class': new_class.to_dict()}), 201
    return jsonify({'message': 'Unauthorized'}), 403

@app.route('/class/<int:class_id>', methods=['PUT'])
@jwt_required()
def update_class(class_id):
    identity = get_jwt_identity()
    if identity['role'] == 'Teacher':  # Or some admin role
        data = request.get_json()
        class_to_update = Class.query.get_or_404(class_id)

        # Ensure that the teacher who created the class is the one updating it
        if class_to_update.teacher_id != identity['id']:
            return jsonify({'message': 'Unauthorized to update this class'}), 403

        class_name = data.get('class_name')
        if class_name:
            class_to_update.class_name = class_name

        db.session.commit()
        return jsonify({'message': 'Class updated successfully', 'class': class_to_update.to_dict()}), 200
    return jsonify({'message': 'Unauthorized'}), 403

@app.route('/class/<int:class_id>', methods=['DELETE'])
@jwt_required()
def delete_class(class_id):
    identity = get_jwt_identity()
    if identity['role'] == 'Teacher':  # Or some admin role
        class_to_delete = Class.query.get_or_404(class_id)

        # Ensure that the teacher who created the class is the one deleting it
        if class_to_delete.teacher_id != identity['id']:
            return jsonify({'message': 'Unauthorized to delete this class'}), 403

        db.session.delete(class_to_delete)
        db.session.commit()
        return jsonify({'message': 'Class deleted successfully'}), 200
    return jsonify({'message': 'Unauthorized'}), 403

@app.route('/classes', methods=['GET'])
@jwt_required()
def get_classes():
    identity = get_jwt_identity()
    print(f"identity {identity}")
    if identity['role'] == 'Teacher':  # Or any authorized role
        classes = Class.query.filter_by(teacher_id=identity.get('id')).all()
        return jsonify([c.to_dict() for c in classes]), 200
    return jsonify({'message': 'Unauthorized'}), 403

@app.route('/subject', methods=['POST'])
@jwt_required()
def create_subject():
    identity = get_jwt_identity()
    if identity['role'] == 'Teacher':  # Or some admin role if applicable
        data = request.get_json()
        subject_name = data.get('subject_name')
        subject_code = data.get('subject_code')
        class_id = data.get('class_id')

        if not (subject_name and subject_code and class_id):
            return jsonify({'message': 'Subject name, code, and class ID are required'}), 400

        new_subject = Subject(subject_name=subject_name, subject_code=subject_code, class_id=class_id, teacher_id=identity['id'])
        db.session.add(new_subject)
        db.session.commit()
        return jsonify({'message': 'Subject created successfully', 'subject': new_subject.to_dict()}), 201
    return jsonify({'message': 'Unauthorized'}), 403

@app.route('/subject/<int:subject_id>', methods=['PUT'])
@jwt_required()
def update_subject(subject_id):
    identity = get_jwt_identity()
    if identity['role'] == 'Teacher':  # Or some admin role
        data = request.get_json()
        subject_to_update = Subject.query.get_or_404(subject_id)

        # Ensure that the teacher who created the subject is the one updating it
        if subject_to_update.teacher_id != identity['id']:
            return jsonify({'message': 'Unauthorized to update this subject'}), 403

        subject_name = data.get('subject_name')
        subject_code = data.get('subject_code')

        if subject_name:
            subject_to_update.subject_name = subject_name
        if subject_code:
            subject_to_update.subject_code = subject_code

        db.session.commit()
        return jsonify({'message': 'Subject updated successfully', 'subject': subject_to_update.to_dict()}), 200
    return jsonify({'message': 'Unauthorized'}), 403

@app.route('/subject/<int:subject_id>', methods=['DELETE'])
@jwt_required()
def delete_subject(subject_id):
    identity = get_jwt_identity()
    if identity['role'] == 'Teacher':  # Or some admin role
        subject_to_delete = Subject.query.get_or_404(subject_id)

        # Ensure that the teacher who created the subject is the one deleting it
        if subject_to_delete.teacher_id != identity['id']:
            return jsonify({'message': 'Unauthorized to delete this subject'}), 403

        db.session.delete(subject_to_delete)
        db.session.commit()
        return jsonify({'message': 'Subject deleted successfully'}), 200
    return jsonify({'message': 'Unauthorized'}), 403

@app.route('/class/<int:class_id>/subjects', methods=['GET'])
@jwt_required()
def get_subjects_for_class(class_id):
    identity = get_jwt_identity()
    if identity['role'] == 'Teacher':  # Or any authorized role
        subjects = Subject.query.filter_by(class_id=class_id, teacher_id=identity['id']).all()
        return jsonify([subject.to_dict() for subject in subjects]), 200
    return jsonify({'message': 'Unauthorized'}), 403

if __name__ == '__main__':
     app.run(port=5555, debug=True)