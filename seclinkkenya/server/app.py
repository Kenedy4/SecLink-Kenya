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
    
    
    return jsonify({"message": "Logged out successfully"}), 200

## Route to manage students ##
def manage_students(student_id):
    identity = get_jwt_identity()  # Retrieve user identity from JWT token

    if identity['role'] == 'Parent':
        if student_id:
            # Parents can only access their own child
            student = Student.query.filter_by(parent_id=identity['id'], id=student_id).first()
            if not student:
                return jsonify({'message': 'Student not found'}), 404
            return jsonify(student.to_dict()), 200
        else:
            # Parents can access all of their own children
            students = Student.query.filter_by(parent_id=identity['id']).all()

    elif identity['role'] == 'Teacher':
        if student_id:
            # Teachers can access any student by ID (in their class, for example)
            student = Student.query.filter_by(id=student_id).first()
            if not student:
                return jsonify({'message': 'Student not found'}), 404
            return jsonify(student.to_dict()), 200
        else:
            # Teachers can access all students, optionally filtering by class_id
            class_id = request.args.get('class_id')
            if class_id:
                students = Student.query.filter_by(class_id=class_id).all()
            else:
                students = Student.query.all()
    else:
        return jsonify({'message': 'Unauthorized'}), 403

    # Build and return the list of students if no specific student_id is provided
    student_list = [{"id": student.id, "name": student.name, "dob": student.dob.isoformat(),
                     "class_id": student.class_id, "overall_grade": student.overall_grade} for student in students]
    return jsonify(student_list), 200

##  Routes to Manage Learning Materials ##
@app.route('/learning-material', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()  # JWT-based authentication
def manage_learning_material():
    identity = get_jwt_identity()  # Get the user's identity from the JWT token

    if request.method == 'GET':
        # Handle retrieving learning materials (Parents only)
        if identity['role'] == 'Parent':
            materials = LearningMaterial.query.all()
            return jsonify([material.to_dict() for material in materials]), 200
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    elif request.method == 'POST':
        # Handle file upload for new learning material (Teachers only)
        if identity['role'] != 'Teacher':
            return jsonify({"message": "Unauthorized access. Only teachers can upload materials."}), 403

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
            learning_material = LearningMaterial(
                title=request.form['title'],  # Title should be in form data
                file_path=file_path,
                teacher_id=identity['id'],  # Use the teacher ID from the JWT identity
                subject_id=request.form.get('subject_id')  # Assuming subject is provided
            )
            db.session.add(learning_material)
            db.session.commit()

            return jsonify({'message': 'Learning material uploaded successfully', 'file_path': file_path}), 200
        else:
            return jsonify({'message': 'Invalid file type'}), 400

    elif request.method == 'PUT':
        # Handle updating an existing learning material (Teachers only)
        if identity['role'] != 'Teacher':
            return jsonify({"message": "Unauthorized access. Only teachers can update materials."}), 403

        if 'id' not in request.form:
            return jsonify({'message': 'Material ID is required'}), 400

        # Find the material by ID
        learning_material = LearningMaterial.query.get(request.form['id'])
        if not learning_material:
            return jsonify({'message': 'Learning material not found'}), 404

        # Ensure the teacher updating the material is the one who uploaded it
        if learning_material.teacher_id != identity['id']:
            return jsonify({'message': 'Unauthorized. You can only update your own materials.'}), 403

        # Update the title if provided
        if 'title' in request.form:
            learning_material.title = request.form['title']

        # Handle file update if a file is provided
        if 'file' in request.files and allowed_file(request.files['file'].filename):
            file = request.files['file']
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(file_path)
                learning_material.file_path = file_path
            except Exception as e:
                return jsonify({'message': f'File could not be saved: {str(e)}'}), 500

        db.session.commit()
        return jsonify({'message': 'Learning material updated successfully'}), 200

    elif request.method == 'DELETE':
        # Handle deleting an existing learning material (Teachers only)
        if identity['role'] != 'Teacher':
            return jsonify({"message": "Unauthorized access. Only teachers can delete materials."}), 403

        material_id = request.form.get('id')  # Assuming 'id' is sent in the form data

        if not material_id:
            return jsonify({'message': 'Material ID is required'}), 400

        # Find the learning material by ID
        learning_material = LearningMaterial.query.get(material_id)
        if not learning_material:
            return jsonify({'message': 'Learning material not found'}), 404

        # Ensure the teacher deleting the material is the one who uploaded it
        if learning_material.teacher_id != identity['id']:
            return jsonify({'message': 'Unauthorized. You can only delete your own materials.'}), 403

        # Delete the file from the server
        try:
            os.remove(learning_material.file_path)  # Remove the file from the file system
        except Exception as e:
            return jsonify({'message': f'File could not be deleted: {str(e)}'}), 500

        # Delete the record from the database
        db.session.delete(learning_material)
        db.session.commit()

        return jsonify({'message': 'Learning material deleted successfully'}), 200

    return jsonify({'message': 'Invalid request method'}), 405  # Handle unsupported methods
@app.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    
# Route to Hanndle Notification ##
@app.route('/notifications', methods=['POST', 'GET'])
@jwt_required()
def manage_notifications():
    identity = get_jwt_identity()

    if request.method == 'POST':
        # Handle adding a notification (Teacher only)
        if identity['role'] == 'Teacher':
            data = request.get_json()
            notification = Notifications(
                message=data['message'],
                parent_id=data['parent_id']
            )
            db.session.add(notification)
            db.session.commit()

            return jsonify({'message': 'Notification sent'}), 200
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    elif request.method == 'GET':
        # Handle getting notifications (Parent only)
        if identity['role'] == 'Parent':
            notifications = Notifications.query.filter_by(parent_id=identity['id']).all()
            return jsonify([notif.to_dict() for notif in notifications]), 200
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    return jsonify({'message': 'Invalid request method'}), 405  # Handle unsupported methods

##  Route To Manage Classes ##

@app.route('/class', methods=['POST', 'PUT', 'DELETE'])
@jwt_required()
def manage_class():
    identity = get_jwt_identity()

    # Check if the user has a 'Teacher' role (or Admin role if applicable)
    if identity['role'] != 'Teacher' and identity['role'] != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403

    if request.method == 'POST':
        # Handle class creation
        data = request.get_json()
        class_name = data.get('class_name')
        if not class_name:
            return jsonify({'message': 'Class name is required'}), 400

        new_class = Class(class_name=class_name, teacher_id=identity['id'])
        db.session.add(new_class)
        db.session.commit()

        return jsonify({'message': 'Class created successfully', 'class': new_class.to_dict()}), 201

    elif request.method == 'PUT':
        # Handle class update
        class_id = request.args.get('class_id')
        if not class_id:
            return jsonify({'message': 'Class ID is required for update'}), 400

        class_to_update = Class.query.get_or_404(class_id)

        # Ensure that the teacher who created the class is the one updating it
        if class_to_update.teacher_id != identity['id']:
            return jsonify({'message': 'Unauthorized to update this class'}), 403

        data = request.get_json()
        class_name = data.get('class_name')
        if class_name:
            class_to_update.class_name = class_name

        db.session.commit()
        return jsonify({'message': 'Class updated successfully', 'class': class_to_update.to_dict()}), 200

    elif request.method == 'DELETE':
        # Handle class deletion
        class_id = request.args.get('class_id')
        if not class_id:
            return jsonify({'message': 'Class ID is required for deletion'}), 400

        class_to_delete = Class.query.get_or_404(class_id)

        # Ensure that the teacher who created the class is the one deleting it
        if class_to_delete.teacher_id != identity['id']:
            return jsonify({'message': 'Unauthorized to delete this class'}), 403

        db.session.delete(class_to_delete)
        db.session.commit()
        return jsonify({'message': 'Class deleted successfully'}), 200

    return jsonify({'message': 'Invalid request method'}), 405  # In case a method other than POST, PUT, or DELETE is used


@app.route('/classes', methods=['GET'])
@jwt_required()
def get_classes():
    identity = get_jwt_identity()

    # Allow teachers to view their own classes and admins to view all classes
    if identity['role'] == 'Teacher':
        classes = Class.query.filter_by(teacher_id=identity['id']).all()
        return jsonify([c.to_dict() for c in classes]), 200
    elif identity['role'] == 'Admin':
        classes = Class.query.all()
        return jsonify([class_.to_dict() for class_ in classes]), 200

    return jsonify({'message': 'Unauthorized'}), 403
@app.route('/subject', methods=['POST', 'PUT', 'DELETE'])
@jwt_required()
def manage_subject():
    identity = get_jwt_identity()

    if request.method == 'POST':
        # Handle creating a new subject (Teacher only)
        if identity['role'] == 'Teacher':
            data = request.get_json()
            subject_name = data.get('subject_name')
            subject_code = data.get('subject_code')
            class_id = data.get('class_id')

            if not (subject_name and subject_code and class_id):
                return jsonify({'message': 'Subject name, code, and class ID are required'}), 400

            new_subject = Subject(
                subject_name=subject_name,
                subject_code=subject_code,
                class_id=class_id,
                teacher_id=identity['id']
            )
            db.session.add(new_subject)
            db.session.commit()

            return jsonify({'message': 'Subject created successfully', 'subject': new_subject.to_dict()}), 201
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    elif request.method == 'PUT':
        # Handle updating a subject (Teacher only)
        if identity['role'] == 'Teacher':
            data = request.get_json()
            subject_id = data.get('subject_id')  # Get subject ID from the request
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
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    elif request.method == 'DELETE':
        # Handle deleting a subject (Teacher only)
        if identity['role'] == 'Teacher':
            subject_id = request.args.get('subject_id')  # Get subject ID from the query string
            subject_to_delete = Subject.query.get_or_404(subject_id)

            # Ensure that the teacher who created the subject is the one deleting it
            if subject_to_delete.teacher_id != identity['id']:
                return jsonify({'message': 'Unauthorized to delete this subject'}), 403

            db.session.delete(subject_to_delete)
            db.session.commit()
            return jsonify({'message': 'Subject deleted successfully'}), 200
        else:
            return jsonify({'message': 'Unauthorized'}), 403

    return jsonify({'message': 'Invalid request method'}), 405  # Handle unsupported methods

@app.route('/class/<int:class_id>/subjects', methods=['GET'])
@jwt_required()
def get_subjects_for_class(class_id):
    identity = get_jwt_identity()

    # Only the teacher who teaches the class can view the subjects for that class
    if identity['role'] == 'Teacher':  # Or any authorized role
        subjects = Subject.query.filter_by(class_id=class_id, teacher_id=identity['id']).all()
        return jsonify([subject.to_dict() for subject in subjects]), 200
    return jsonify({'message': 'Unauthorized'}), 403

if __name__ == '__main__':
     app.run(port=5555, debug=True)